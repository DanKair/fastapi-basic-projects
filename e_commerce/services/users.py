from pwdlib import PasswordHash
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from models.users import User, UserRole

# Initialize the hasher with recommended settings (Argon2)
password_hash = PasswordHash.recommended()

def get_user_by_username_or_email(db: Session, username: str, email: str):
    """Return a user matching the provided username or email."""
    result = db.execute(
        select(User).where(or_(User.username == username, User.email == email))
    )
    return result.scalars().first()


def get_user_by_identifier(db: Session, identifier: str) -> User | None:
    """Return a user matching the provided identifier"""
    result = db.execute(
        select(User).where(or_(User.username == identifier, User.email == identifier))
    )
    return result.scalars().first()

def get_user_by_username(db: Session, username: str) -> User | None:
    result = db.execute(
        select(User).where(User.username == username)
    )
    return result.scalars().first()


def authenticate_user(db: Session, identifier: str, password: str) -> User | None:
    user = get_user_by_identifier(db, identifier)
    if not user:
        return None
    return user if verify_password(password, user.password_hash) else None


def create_user(
    db: Session,
    *,
    username: str,
    email: str,
    password: str,
    role: UserRole = UserRole.CUSTOMER,
) -> User:
    existing_user = get_user_by_username_or_email(db, username=username, email=email)
    if existing_user:
        if existing_user.username == username:
            detail = "Username already exists"
        elif existing_user.email == email:
            detail = "Email already registered"
        else:
            detail = "User with given credentials already exists"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    new_user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        role=role.value,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_password_hash(password: str) -> str:
    """Returns a hashed version of the plain password."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the plain password matches the stored hash."""
    return password_hash.verify(plain_password, hashed_password)


