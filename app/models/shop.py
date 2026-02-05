from app.extensions.db import db
from .base import BaseModel
from datetime import datetime, timezone


class Shop(BaseModel):
    __tablename__ = "shops"

    owner_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id"),
        nullable=False
    )
    name = db.Column(db.String(150), nullable=False)
    logo = db.Column(db.String(255))
    banner = db.Column(db.String(255))
    rating = db.Column(db.Numeric(3, 2), default=0.00)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
