from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from schemas.categories import CategoryCreate, CategoryUpdate
from models.categories import Category

class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def category_exists(self, category_id_to_check: int, db: Session):
        category_exists = self.db.execute(
            select(Category.id).where(Category.id == category_id_to_check)
        ).scalar_one_or_none()

        if not category_exists:
            raise HTTPException(
                status_code=404,
                detail=f"Category with id '{category_id_to_check}' does not exist.",
            )
        return True


    def get_all(self) -> List[Category]:
        """Returns all existing categories"""
        return self.db.execute(select(Category)).scalars().all()
    

    def get_by_id(self, category_id: int) -> Category:
        category = self.category_exists(category_id)
        if category:
            return self.db.execute(select(Category).where(Category.id == category_id)).scalar_one_or_none()
    
    
    def create(self, category_data: CategoryCreate) -> Category:
        """Checks if following category already exists, then create new one after validation"""
        existing = self.db.execute(
            select(Category).where(Category.name == category_data.name)
        ).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Category with this name already exists.",
            )

        new_category = Category(**category_data.model_dump())
        self.db.add(new_category)
        self.db.commit()
        self.db.refresh(new_category)
        return new_category
    
    
    def update(self, category_id: int, category_update: CategoryUpdate) -> Category:
        category = self.get_by_id(category_id)

        update_data = category_update.model_dump(exclude_unset=True)

        if "name" in update_data:
            duplicate = self.db.execute(
                select(Category).where(
                    Category.name == update_data["name"], 
                    Category.id != category_id
                )
            ).scalar_one_or_none()

            if duplicate:
                raise HTTPException(
                    status_code=400,
                    detail="Category with this name already exists.",
                )

        for key, value in update_data.items():
            setattr(category, key, value)

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
    

    def delete(self, category_id: int) -> None:
        """Using get_by_id method to check if following category exists"""
        category = self.get_by_id(category_id)
        self.db.delete(category)
        self.db.commit()
