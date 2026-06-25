from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.customers import Customer

class UserRole(str, Enum):
    CUSTOMER = "customer"  # Shopper buying groceries
    MANAGER = "manager"    # Staff handling the shop (warehouse/catalog/orders)
    ADMIN = "admin"        # Full system access (manage users, roles, etc.)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[UserRole] = mapped_column(String, nullable=False, default=UserRole.CUSTOMER)
    is_active: Mapped[bool] = mapped_column(default=True)
    # Timestamping for auditing
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    # uselist=False tells SQLAlchemy this is a strict 1:1, not 1:Many
    customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="user", uselist=False)
    
