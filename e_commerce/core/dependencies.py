from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from models.users import User, UserRole
from .database import get_db
from services.products import ProductService
from services.categories import CategoryService
from services.auth import get_current_user

def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

    
class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not current_user.is_active:
            raise HTTPException(
                status_code=401, 
                detail="User account is inactive"
            )
            
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have enough permissions to access this resource"
            )
            
        return current_user 

require_admin = RoleChecker([UserRole.ADMIN]) 
require_editoral = RoleChecker([UserRole.ADMIN, UserRole.MANAGER])    
