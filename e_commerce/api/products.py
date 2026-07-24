from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from core.dependencies import get_product_service, require_editoral
from services.products import ProductService, SortOrder
from schemas.products import PaginatedProductEnvelope, ProductCreate, ProductResponse, ProductUpdate


router = APIRouter(prefix='/products', tags=['products'])

UPLOAD_DIRECTORY = Path(__file__).resolve().parent.parent / "uploads" / "products"
MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "image/webp": {".webp"},
}

@router.post("/create", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_editoral)])
def create_new_product(
    product_data: Annotated[ProductCreate, Form()],
    service: Annotated[ProductService, Depends(get_product_service)]
):
    return service.create(product_data)


@router.get("/", response_model=PaginatedProductEnvelope, status_code=status.HTTP_200_OK)
def get_all_products(
    service: Annotated[ProductService, Depends(get_product_service)],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
):
    return service.get_paginated(page=page, size=size)

@router.get("/{order_type}/price")
def get_products_by_price(
    service: Annotated[ProductService, Depends(get_product_service)],
    order_type: SortOrder
):
    return service.order_by_price(order_type)


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


@router.delete("/category/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_editoral)])
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


@router.patch("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(require_editoral)])
def update_product(
    product_id: int,
    product_update: Annotated[ProductUpdate, Form()],
    service: Annotated[ProductService, Depends(get_product_service)]
):
    return service.update(product_id, product_update)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_editoral)])
def delete_product(
    product_id: int,
    service: Annotated[ProductService, Depends(get_product_service)]
):
    return service.delete(product_id)

@router.post(
    "/{product_id}/image",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_editoral)],
)
def upload_product_image(
    product_id: int,
    image: Annotated[UploadFile, File(...)],
    service: Annotated[ProductService, Depends(get_product_service)],
):
    """Upload or replace a product image for editorial users."""
    content_type = image.content_type or ""
    allowed_extensions = ALLOWED_IMAGE_TYPES.get(content_type)
    extension = Path(image.filename or "").suffix.lower()

    if not allowed_extensions or extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPG, PNG, and WEBP images are supported.",
        )

    # Check the product before creating a file that could otherwise be orphaned.
    product = service.get_by_id(product_id)
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}{extension}"
    destination = UPLOAD_DIRECTORY / filename
    bytes_written = 0

    previous_path = product.image_path

    try:
        with destination.open("wb") as output:
            while chunk := image.file.read(1024 * 1024):
                bytes_written += len(chunk)
                if bytes_written > MAX_IMAGE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Product image must not exceed 5 MB.",
                    )
                output.write(chunk)

        relative_path = f"uploads/products/{filename}"
        product = service.update_image_path(product_id, relative_path)

        if previous_path:
            previous_file = Path(__file__).resolve().parent.parent / previous_path
            if previous_file.parent == UPLOAD_DIRECTORY:
                previous_file.unlink(missing_ok=True)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        image.file.close()

    return product
