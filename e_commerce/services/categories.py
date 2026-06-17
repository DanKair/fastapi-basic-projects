from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.categories import Category


def category_exists(category_id_to_check: int, db: Session):
    category_exists = db.execute(
        select(Category.id).where(Category.id == category_id_to_check)
    ).scalar_one_or_none()

    if not category_exists:
        raise HTTPException(
            status_code=404,
            detail=f"Category with id '{category_id_to_check}' does not exist.",
        )
    return True