from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.products import Product


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[String] = mapped_column(String, nullable=False)

    products: Mapped[List["Product"]] = relationship(back_populates="category")