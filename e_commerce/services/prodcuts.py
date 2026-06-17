from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.categories import Category
from models.products import Product

def fetch_product_by_category_id(category_id: int, db: Session):
    stmt = select(Product).where(Product.category_id == category_id)
    result = db.execute(stmt).scalars().all()
    return result


def fetch_product_by_category_name(category_name: str, db: Session):
    """
    Fetches all products matching a specific category string name.
    """
    stmt = (
        select(Product)
        .join(Category)
        .where(Category.name == category_name)
    )
    return db.execute(stmt).scalars().all()


def product_exists(product_name, product_category_id, db: Session):
    """
    Checks if product already exists if both Product Name and Category matchess
    """
    existing_product = db.execute(
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
    
