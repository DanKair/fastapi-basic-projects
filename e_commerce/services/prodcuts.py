from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from e_commerce.schemas.products import ProductCreate
from models.categories import Category
from models.products import Product


class ProductService:
    def __init__(self, db: Session):
        self.db = db


    def _category_exists(self, category_id: int) -> bool:
        """Internal Helper method to check existance of category"""
        exists = self.db.execute(
            select(Category.id).where(Category.id == category_id)
        ).scalar_one_or_none()

        if not exists:
            raise HTTPException(
                status_code=404,
                detail=f"Category with id '{category_id}' does not exist.",
            )
        return True        


    def get_all(self) -> List[Product]:
        products = self.db.execute(select(Product)).scalars().all()
        return products

    def get_by_category_id(self, category_id: int) -> List[Product]:
        stmt = select(Product).where(Product.category_id == category_id)
        result = self.db.execute(stmt).scalars().all()
        return result


    def get_by_category_name(self, category_name: str) -> List[Product]:
        """
        Fetches all products matching a specific category string name.
        """
        stmt = (
            select(Product)
            .join(Category)
            .where(Category.name == category_name)
        )
        return self.db.execute(stmt).scalars().all()


    def product_exists(self, product_name, product_category_id):
        """
        Checks if product already exists if both Product Name and Category matchess
        """
        existing_product = self.db.execute(
            select(Product).where(
                Product.name == product_name,
                Product.category_id == product_category_id,
            )
        ).scalar_one_or_none()

        if existing_product:
            raise HTTPException(
                status_code=400,
                detail="A product with this name already exists in this category."
            )
        return False
    

    def create_new_product(self, product_data: ProductCreate):
        # 0. Validate that chosen category exists
        if self._category_exists(product_data.category_id):
            # 1. Check if following product already exists
            if not self.product_exists(product_data.name, product_data.category_id):
                # 2. Dynamically unpack the data into the SQLAlchemy model
                new_product = Product(**product_data.model_dump())

                # 3. Save to the database
                self.db.add(new_product)
                try:
                    self.db.commit()
                    self.db.refresh(new_product)  # Populates the generated 'id' field
                except Exception as e:
                    self.db.rollback()
                    raise HTTPException(
                        status_code=400, 
                        detail="Could not create product. Check foreign keys or constraints."
                    )

                return new_product
        
