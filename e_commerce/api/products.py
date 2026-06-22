from typing import Annotated

from fastapi import APIRouter, Depends, Form, status
from core.dependencies import get_product_service
from services.products import ProductService
from schemas.products import ProductCreate, ProductResponse, ProductUpdate


router = APIRouter(prefix='/products', tags=['products'])

@router.post("/create", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_new_product(
    product_data: Annotated[ProductCreate, Form()],
    service: Annotated[ProductService, Depends(get_product_service)]
):
    return service.create(product_data)


@router.get("/", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def get_all_products(service: Annotated[ProductService, Depends(get_product_service)]):
    return service.get_all()


@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product_by_id(
    product_id: int,
    service: Annotated[ProductService, Depends(get_product_service)]
):
    return service.get_by_id(product_id)


@router.get("/category/{category_id}", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def get_by_category(
    category_id: int,
    service: Annotated[ProductService, Depends(get_product_service)]
):
    return service.get_by_category_id(category_id)


@router.delete("/category/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_products_by_category(
    category_id: int,
    service: Annotated[ProductService, Depends(get_product_service)]
):
    return service.delete_by_category(category_id)


@router.get("/search/{category_name}", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def get_by_category_name(
    category_name: str,
    service: Annotated[ProductService, Depends(get_product_service)]
):
    return service.get_by_category_name(category_name)


@router.patch("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(
    product_id: int,
    product_update: Annotated[ProductUpdate, Form()],
    service: Annotated[ProductService, Depends(get_product_service)]
):
    return service.update(product_id, product_update)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    service: Annotated[ProductService, Depends(get_product_service)]
):
    return service.delete(product_id)