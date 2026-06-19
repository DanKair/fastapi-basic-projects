from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from services.prodcuts import ProductService
from services.categories import CategoryService

def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)
