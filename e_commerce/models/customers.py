from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.orders import Order
from models.users import User


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    shipping_address: Mapped[str] = mapped_column(String(500))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="customer")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="customer")