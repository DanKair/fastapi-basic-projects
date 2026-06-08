from decimal import Decimal
from enum import Enum
from typing import List

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.customers import Customer
from models.order_items import OrderItem
from core.database import Base


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    # Use asdecimal=True to force strict Decimal handling in SQLite
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2, asdecimal=True))
    order_status: Mapped[OrderStatus] = mapped_column()

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="orders")
    # cascade="all, delete-orphan" means if an Order is deleted, its line items are deleted too
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
