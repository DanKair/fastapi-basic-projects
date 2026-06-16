from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db


router = APIRouter(prefix='/products', tags=['products'])

@router.get("/")
def get_all_products(db: Annotated[Session, Depends(get_db)]):
    pass