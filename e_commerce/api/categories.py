from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from core.database import get_db
from models.categories import Category
from schemas.categories import CategoryCreate, CategoryResponse, CategoryUpdate


router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/create", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Annotated[Session, Depends(get_db)],
):
    existing_category = db.execute(
        select(Category).where(Category.name == category_data.name)
    ).scalar_one_or_none()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists.",
        )

    new_category = Category(**category_data.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.get("", response_model=List[CategoryResponse], status_code=status.HTTP_200_OK)
def get_all_categories(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Category))
    return result.scalars().all()


@router.get("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def get_category_by_id(category_id: int, db: Annotated[Session, Depends(get_db)]):
    category = db.execute(
        select(Category).where(Category.id == category_id)
    ).scalar_one_or_none()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id '{category_id}' does not exist.",
        )

    return category


@router.patch("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    category = db.execute(
        select(Category).where(Category.id == category_id)
    ).scalar_one_or_none()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id '{category_id}' does not exist.",
        )

    update_data = category_update.model_dump(exclude_unset=True)

    if "name" in update_data:
        duplicate_category = db.execute(
            select(Category).where(Category.name == update_data["name"], Category.id != category_id)
        ).scalar_one_or_none()

        if duplicate_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists.",
            )

    for key, value in update_data.items():
        setattr(category, key, value)

    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Annotated[Session, Depends(get_db)]):
    category = db.execute(
        select(Category).where(Category.id == category_id)
    ).scalar_one_or_none()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id '{category_id}' does not exist.",
        )

    db.delete(category)
    db.commit()
    return None
