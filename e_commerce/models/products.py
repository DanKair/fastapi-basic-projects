from decimal import Decimal
from typing import List

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.order_items import OrderItem


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2)) # Used for production database
    stock_quantity: Mapped[int]

    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")