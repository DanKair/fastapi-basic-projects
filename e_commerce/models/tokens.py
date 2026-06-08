from datetime import datetime, timezone
import uuid
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    # JWT ID - unique identifier of the token
    jti: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # Foreign key linking to User model
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
     # Expiration timestamp
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), # Enforces TIMESTAMP WITH TIME ZONE in Postgres
        nullable=False,
        server_default=func.now(), # Uses the central DB clock for perfect accuracy
    )