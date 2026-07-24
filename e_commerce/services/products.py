from enum import Enum
from typing import List
from fastapi import HTTPException
from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Session

from schemas.products import PaginatedProductEnvelope, ProductCreate, ProductUpdate
from models.categories import Category
from models.products import Product


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def _category_exists(self, category_id: int) -> bool:
        """Internal Helper method to check existence of category."""
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

    def get_paginated(self, page: int, size: int) -> PaginatedProductEnvelope:
        if page < 1:
            raise HTTPException(status_code=400, detail="Page must be at least 1")
        if size < 1:
            raise HTTPException(status_code=400, detail="Size must be at least 1")

        total_products = self.db.execute(select(Product)).scalars().count()

        stmt = (
            select(Product)
            .offset((page - 1) * size)
            .limit(size)
        )
        products = self.db.execute(stmt).scalars().all()

        total_pages = (total_products + size - 1) // size if total_products else 1

        return PaginatedProductEnvelope(
            products=products,
            total_products=total_products,
            page=page,
            size=size,
            total_pages=total_pages,
        )

    def get_by_id(self, product_id: int) -> Product:
        product = self.db.execute(
            select(Product).where(Product.id == product_id)
        ).scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with id '{product_id}' does not exist.",
            )

        return product

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
            .where(Category.name.ilike(f"{category_name}%"))
        )
        return self.db.execute(stmt).scalars().all()
    
    def order_by_price(self, order_type: SortOrder):
        """Orders products by their prices in DESCENDING ORDER"""
        if order_type == "desc":
            stmt = (
                select(Product)
                .order_by(desc(Product.price))
            )
            return self.db.execute(stmt).scalars().all()
        
        return self.db.execute(select(Product).order_by(Product.price)).scalars().all()

    def product_exists(self, product_name, product_category_id):
        """
        Checks if product already exists if both Product Name and Category match.
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

    def create(self, product_data: ProductCreate):
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
                except Exception:
                    self.db.rollback()
                    raise HTTPException(
                        status_code=400,
                        detail="Could not create product. Check foreign keys or constraints.",
                    )

                return new_product

    def update(self, product_id: int, product_update: ProductUpdate):
        product = self.get_by_id(product_id)
        update_data = product_update.model_dump(exclude_unset=True)

        if "category_id" in update_data:
            self._category_exists(update_data["category_id"])

        if "name" in update_data or "category_id" in update_data:
            new_name = update_data.get("name", product.name)
            new_category_id = update_data.get("category_id", product.category_id)
            duplicate = self.db.execute(
                select(Product).where(
                    Product.name == new_name,
                    Product.category_id == new_category_id,
                    Product.id != product_id,
                )
            ).scalar_one_or_none()

            if duplicate:
                raise HTTPException(
                    status_code=400,
                    detail="A product with this name already exists in this category.",
                )

        for key, value in update_data.items():
            setattr(product, key, value)

        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update_image_path(self, product_id: int, image_path: str) -> Product:
        product = self.get_by_id(product_id)
        product.image_path = image_path
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: int) -> None:
        product = self.get_by_id(product_id)
        self.db.delete(product)
        self.db.commit()

    def delete_by_category(self, category_id: int) -> None:
        self._category_exists(category_id)

        stmt = delete(Product).where(Product.category_id == category_id)
        self.db.execute(stmt)
        self.db.commit()


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"        

