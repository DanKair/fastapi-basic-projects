from fastapi import APIRouter, Cookie, Depends, Response, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from models.users import User
from schemas.auth import TokenPairsResponse, UserRegister
from services.auth import add_token_to_blacklist, create_access_token, create_refresh_token, get_current_user, is_refresh_token_expired, revoke_refresh_token, get_refresh_token_record, oauth2_scheme
from services.users import authenticate_user, get_password_hash, get_user_by_username_or_email

# Centralized cookie configuration helper
def set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        key="refresh_token",
        value=token,    
        httponly=True, # Prevents XSS attacks (JS cannot read it)
        max_age=settings.REFRESH_TOKEN_AGE_SECONDS,
        samesite="lax",
        secure=settings.HTTPS_ENABLED # Ensures the cookie is only transmitted over HTTPS
    )


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("", response_model=TokenPairsResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserRegister, db: Annotated[Session, Depends(get_db)],  response: Response):
    """
    Corrected Register Flow:
    1. Check if user already exists.
    2. Hash the user's password.
    3. Create and commit the User model to generate an ID.
    4. Generate the Access Token (JWT) and raw Refresh Token.
    5. Hash the Refresh Token and save it using the new user's ID.
    6. Return the tokens.
    """

    # 1.    Check if user exists
    existing_user = get_user_by_username_or_email(db, user.username, user.email)
    if existing_user:
        if existing_user.username == user.username:
            detail = "Username already exists"
        elif existing_user.email == user.email:
            detail = "Email already registered"
        else:
            detail = "User with given credentials already exists"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
    
     # 2. Hash password and save the User first
    password = get_password_hash(user.password)
    new_user = User(username=user.username, email=user.email, password_hash=password)
    db.add(new_user)
    
    # We commit here so the database generates the new_user.id
    db.commit()
    db.refresh(new_user) # Now new_user.id is fully accessible in Python
    
    # 3. Create and save Refresh token using the newly generated user_id
    refresh_token = create_refresh_token(new_user.id, db) 

    # Save refresh token in cookies
    set_refresh_cookie(response, refresh_token)
    

    # 4. Extract database record to capture the auto-generated JTI
    record = get_refresh_token_record(refresh_token, db)

    # 5. Create stateless access token containing the unique token/session identifier
    access_token = create_access_token({"sub": user.username, "jti": str(record.jti)})

    # 6. Return generated token pairs
    token_pairs = TokenPairsResponse(access_token=access_token, refresh_token=refresh_token)


    return token_pairs

    

   
@router.post("/login", response_model=TokenPairsResponse)
def user_login(user: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)], response: Response):
    """
    Algorithm FLOW:
    1. Verify that the user exists
    2. Verify credentials against the database
    3. Generate access token and refresh token
    4. Store refresh token in DB with hash
    5. Return both tokens
    """
    authenticated_user = authenticate_user(db, user.username, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate refresh token and save it in cookies
    refresh_token = create_refresh_token(user_id=authenticated_user.id, db=db)
    set_refresh_cookie(response, token=refresh_token)

    # Extract database record to capture the auto-generated JTI
    record = get_refresh_token_record(refresh_token, db)

    # Create final access token using extracted record's JTI
    access_token = create_access_token(
        {
            "sub": authenticated_user.username, 
            "jti": str(record.jti) 
        }
    )
    
    return TokenPairsResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenPairsResponse)
def refresh_session(
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    # 1. Automatically extracts the raw token string from the browser cookies
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    """
    Refresh Flow:
    0. Executes only when access token expires or becomes revoked
    1. Verify cookie presence.
    2. Hash incoming token to match database storage formatting.
    3. Query the DB by hash to instantly verify existence and find the user.
    4. Validate expiration.
    5. Issue a new access token (and optionally rotate the refresh token).
    """
    # Step 1: Ensure the token cookie was actually sent
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing from request cookies"
        )
    
    # Step 2: Get record of the token
    # Automatically throws credentials_exception if missing or safe compare fails
    session_record = get_refresh_token_record(refresh_token, db)
    

    # Step 3: Verify the token hasn't expired yet
    # Compare database timestamp against current UTC time
    if is_refresh_token_expired(refresh_token, db):
        # Revokation Scenario 1: Remove token from db if it's expired
        revoke_refresh_token(refresh_token, db)
        # Clear the cookie also     
        response.delete_cookie("refresh_token", path="/auth")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired. Please log in again."
        )
        
    # Fetch the user to get their username for the access token "sub" claim
    user = db.query(User).filter(User.id == session_record.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated or missing"
        )

    # Revokation Scenario 2: Token rotation (Creating new token and removing existing ones)
    revoke_refresh_token(refresh_token, db)

    # Create refresh token and extract its record from db for jti use
    new_refresh_token = create_refresh_token(user_id=user.id, db=db)
    
    # Set the new refresh token in httponly cookie
    set_refresh_cookie(response, token=new_refresh_token)

    new_record = get_refresh_token_record(new_refresh_token, db)
    # Step 5: Issue a fresh short-lived access token and set jti field to newly created access token
    new_access_token = create_access_token({"sub": user.username, "jti": str(new_record.jti)})

    # Return the payload back to the client
    return TokenPairsResponse(
        access_token=new_access_token, 
        refresh_token=new_refresh_token
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    db: Annotated[Session, Depends(get_db)],
    response: Response,
    # access_token: Annotated[str, Depends(oauth2_scheme)], # Comment this if testing
    refresh_token: Annotated[str | None, Cookie()] = None
) -> dict:
    """
    Logout and revoke refresh token.
    
    REVOCATION SCENARIO 3: User explicitly logs out.
    - Extracts refresh token from cookie
    - Deletes the token record from database
    - Clears the refresh token cookie
    """

    # Add access token to blacklist
    #add_token_to_blacklist(access_token)

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No refresh token found in cookies"
        )
    
    # Attempt to revoke the token from database
    try:
        revoke_refresh_token(token=refresh_token, db=db)
    except HTTPException as e:
        response.delete_cookie("refresh_token")
        raise e
    # Remove the token from cookies anyways
    response.delete_cookie("refresh_token")
    
    return {"detail": "Successfully logged out. Refresh token revoked."}