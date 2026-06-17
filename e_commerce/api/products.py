from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from services.categories import category_exists
from services.prodcuts import product_exists
from models.products import Product
from schemas.products import ProductCreate


router = APIRouter(prefix='/products', tags=['products'])

@router.post("/create")
def create_new_product(product_data: ProductCreate, db: Annotated[Session, Depends(get_db)]):
    if category_exists(product_data.category_id):
        # 0. Check if following product already exists
        if not product_exists(product_data.name, product_data.category_id):
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
def get_all_products(db: Annotated[Session, Depends(get_db)]):
    pass