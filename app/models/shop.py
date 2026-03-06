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

    # =====================
    # SHIPPING SETTINGS
    # =====================
    shipping_fast = db.Column(db.Boolean, default=True)
    shipping_same_day = db.Column(db.Boolean, default=True)
    shipping_express = db.Column(db.Boolean, default=True)
    shipping_self_delivery = db.Column(db.Boolean, default=False)
    shipping_bulky = db.Column(db.Boolean, default=False)

    shipping_configured = db.Column(db.Boolean, default=False)

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    owner = db.relationship(
    "User",
    backref=db.backref("shop", uselist=False)
)