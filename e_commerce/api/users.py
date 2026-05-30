
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.database import get_db
from models.users import User
from schemas.users import UserResponse, UserUpdate
from services.auth import  get_current_user
from services.users import (
    get_password_hash,
    verify_password
)


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def get_all_users(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/update", response_model=UserResponse)
def user_update(
    user_update: UserUpdate, 
    db: Annotated[Session, Depends(get_db)], 
    current_user: User = Depends(get_current_user)
    ):
    # 1. Make sure user is logged in
    # 2. Make user view his profile data
    # 3. Update his data
    
    # 1. Convert schema to dict, keeping ONLY what the user sent
    update_data = user_update.model_dump(exclude_unset=True)

    # 2. Handle Password field specifically
    if "new_password" in update_data:
        # Explicitly check for None to satisfy type checkers
        if user_update.old_password is None:
            raise HTTPException(status_code=400, detail="Old password is required")

        if not verify_password(user_update.old_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="Invalid old password")
        
        # Hash the new password and replace it in the update dict
        if user_update.new_password is None:
            raise HTTPException(status_code=400, detail="New Password should be provided")
        current_user.password_hash = get_password_hash(user_update.new_password)
        
        # Remove password fields so they aren't processed in the general loop
        update_data.pop("new_password")
        update_data.pop("old_password")

    # 3. Apply remaining fields (username, email) to the DB object
    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user
        


    
