from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from e_commerce.core.dependencies import get_product_service
from services.categories import category_exists
from services.prodcuts import ProductService, product_exists
from models.products import Product
from schemas.products import ProductCreate


router = APIRouter(prefix='/products', tags=['products'])

@router.post("/create")
def create_new_product(product_data: ProductCreate, db: Annotated[Session, Depends(get_db)]):
    if category_exists(product_data.category_id, db):
        # 0. Check if following product already exists
        if not product_exists(product_data.name, product_data.category_id, db):
            # 1. Dynamically unpack the data into the SQLAlchemy model
            new_product = Product(**product_data.model_dump())

            # 2. Save to the database
            db.add(new_product)
            try:
                db.commit()
                db.refresh(new_product)  # Populates the generated 'id' field
            except Exception as e:
                db.rollback()
                raise HTTPException(
                    status_code=400, 
                    detail="Could not create product. Check foreign keys or constraints."
                )

            return new_product


@router.get("/")
def get_all_products(service: Annotated[ProductService, Depends(get_product_service)]):
    return service.get_all()


@router.get("/category/{category_id}")
def get_by_category(category_id: int, service: Annotated[ProductService, Depends(get_product_service)]):
    return service.get_by_category_id(category_id)


@router.get("category-name/{category_name}")
def get_by_category_name(category_name: str, service: Annotated[ProductService, Depends(get_product_service)]):
    return service.get_by_category_name(category_name)