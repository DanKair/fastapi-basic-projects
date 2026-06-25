from typing import Annotated, List
from fastapi import APIRouter, Depends, status

from core.dependencies import get_category_service, require_editoral
from services.categories import CategoryService
from schemas.categories import CategoryCreate, CategoryResponse, CategoryUpdate


router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/create", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_editoral)])
def create_category(
    category_data: CategoryCreate,
    service: Annotated[CategoryService, Depends(get_category_service)],
):
    return service.create(category_data)


@router.get("", response_model=List[CategoryResponse], status_code=status.HTTP_200_OK)
def read_all_categories(service: Annotated[CategoryService, Depends(get_category_service)]):
    return service.get_all()


@router.get("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def read_category_by_id(
    category_id: int,
    service: Annotated[CategoryService, Depends(get_category_service)]
):
    return service.get_by_id(category_id)


@router.patch("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(require_editoral)])
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    service: Annotated[CategoryService, Depends(get_category_service)],
):
    return service.update(category_id, category_update)
    

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_editoral)])
def delete_category(
    category_id: int,
    service: Annotated[CategoryService, Depends(get_category_service)]
):
    return service.delete(category_id)
