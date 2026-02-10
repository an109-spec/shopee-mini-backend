from app.extensions.db import db
from .base import BaseModel
from datetime import datetime, timezone

class Order(BaseModel):
    __tablename__ = "orders"

    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    total_price = db.Column(db.Numeric(12, 2))
    status = db.Column(
        db.Enum("pending", "preparing", "shipping", "delivered", "cancelled", name="order_status")
    )
    payment_method=db.Column(db.Enum("COD", "SHOP", "QR"))

class OrderItem(BaseModel):
    __tablename__ = "order_items"

    order_id = db.Column(db.BigInteger, db.ForeignKey("orders.id"))
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id"))
    price = db.Column(db.Numeric(12, 2))
    quantity = db.Column(db.Integer)

class OrderTracking(BaseModel):
    __tablename__ = "order_tracking"

    order_id = db.Column(
        db.BigInteger,
        db.ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )
    status = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
