import re
from unittest import result

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

