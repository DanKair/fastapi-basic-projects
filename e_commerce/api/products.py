from typing import Annotated

from fastapi import APIRouter, Depends, Form
from core.dependencies import get_product_service
from services.products import ProductService
from schemas.products import ProductCreate


router = APIRouter(prefix='/products', tags=['products'])

@router.post("/create")
def create_new_product(product_data: Annotated[ProductCreate, Form()], service: Annotated[ProductService, Depends(get_product_service)]):
   return service.create(product_data)


@router.get("/")
def get_all_products(service: Annotated[ProductService, Depends(get_product_service)]):
    return service.get_all()


@router.get("/category/{category_id}")
def get_by_category(category_id: int, service: Annotated[ProductService, Depends(get_product_service)]):
    return service.get_by_category_id(category_id)


@router.get("category-name/{category_name}")
def get_by_category_name(category_name: str, service: Annotated[ProductService, Depends(get_product_service)]):
    return service.get_by_category_name(category_name)