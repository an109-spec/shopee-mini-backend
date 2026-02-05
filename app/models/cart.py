from app.extensions.db import db
from .base import BaseModel
from datetime import datetime, timezone

class Cart(BaseModel):
    __tablename__ = "carts"

    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), unique=True)
    updated_at=db.column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class CartItem(BaseModel):
    __tablename__ = "cart_items"

    cart_id = db.Column(db.BigInteger, db.ForeignKey("carts.id"))
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id"))
    quantity = db.Column(db.Integer, nullable=False)
