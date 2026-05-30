from enum import Enum
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.order_items import OrderItem
from models.users import Base


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    total_price: Mapped[float] = mapped_column()
    order_status: Mapped[OrderStatus] = mapped_column()

    items: Mapped[List["OrderItem"]] = relationship(back_populates="order")
