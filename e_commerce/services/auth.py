import hashlib, jwt
from secrets import token_urlsafe, compare_digest
from typing import Annotated

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone

from pydantic import ValidationError
from sqlalchemy.orm import Session
from core.config import settings
from core.database import get_db
from exceptions.auth import credentials_exception
from models.tokens import RefreshToken
from services.users import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Creates a JWT access token.

    Args:
        data (dict): The data to encode in the JWT.
        expires_delta (timedelta | None, optional): The time duration until the token expires. Defaults to 15 minutes if not provided.

    Returns:
        str: The encoded JWT token as a string.
    """
    # Making copy of passed data
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update(exp=expire)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        # Decodes and validates the signature and expiration (exp)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_jti(token: str = Depends(oauth2_scheme)) -> str:
    try:
        # Decode the token payload
        payload = decode_access_token(token)
        
        # Extract the jti claim
        jti = payload.get("jti")
        
        if jti is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing jti claim",
            )
        return jti
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session):
    try:
        # Decode the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload["sub"]
        if not username:
            raise credentials_exception
        
        # Check if following user exist in db by username
        user = get_user_by_username(db, username)
        if not user:
            raise credentials_exception
        return user

    except (jwt.PyJWTError, jwt.ExpiredSignatureError):
        # Handle invalid or expired tokens
        raise credentials_exception
    

def generate_refresh_token() -> str:
    """Generates a long-lived, high-entropy random string (Opaque Token)."""
    return token_urlsafe(32)


def _hash_token(token: str) -> str:
    """Centralized utility to safely hash opaque tokens."""
    return hashlib.sha256(token.encode()).hexdigest()


def get_refresh_token_record(token: str, db: Session) -> RefreshToken:
    """Helper to fetch record and protect against timing attacks."""
    target_hash = _hash_token(token)
    # Fetch using hash lookup first
    record = db.query(RefreshToken).filter(RefreshToken.token_hash == target_hash).first()
    
    if not record or not compare_digest(record.token_hash, target_hash):
        raise credentials_exception
    return record


def is_refresh_token_expired(token: str, db: Session):
    session_record = get_refresh_token_record(token, db)

    if not session_record:
        raise ValidationError("Token doesn't exist")

    return True if datetime.now(timezone.utc) > session_record.expires_at.replace(tzinfo=timezone.utc) else False


def revoke_refresh_token(token: str, db: Session):
    """
    Revokes (deletes) a refresh token from the database.
    
    Args:
        token: The plain refresh token string to revoke
        db: Database session
    
    Raises:
        HTTPException: If token doesn't exist
    """
    # Get session record
    record = get_refresh_token_record(token, db)

    
    # Delete and commit
    db.delete(record)
    db.commit()



def create_refresh_token(user_id: int, db: Session):
    # 3. Create and save Refresh token using the newly generated user_id
    generated_token = generate_refresh_token()
    token_expiry = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    # Save user to databse
    refresh_token = RefreshToken(
        user_id=user_id, 
        token_hash=_hash_token(generated_token), 
        expires_at=token_expiry
    )
    db.add(refresh_token)
    db.commit()
    # Returns plain generated token instead of our newly created model
    return generated_token
    


def refresh_session(refresh_token: str):
    """
    1. Validates refresh token against db (Check if passed value has matching hash)
    2. Check expiration date of the passed token
    3. Create new access token and return it
    """
    pass