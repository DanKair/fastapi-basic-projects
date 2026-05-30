from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.order_items import OrderItem
from models.users import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[float]
    stock_quantity: Mapped[int]

    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")