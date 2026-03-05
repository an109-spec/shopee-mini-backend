from app.extensions.db import db
from .base import BaseModel


class Payment(BaseModel):
    __tablename__ = "payments"

    order_id = db.Column(
        db.BigInteger,
        db.ForeignKey("orders.id"),
        nullable=False,
        index=True
    )

    method = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), default="PENDING", index=True)

    transaction_code = db.Column(db.String(100), unique=True)

    amount = db.Column(db.Numeric(12,2), nullable=False)

    provider = db.Column(db.String(50))

    paid_at = db.Column(db.DateTime)

    order = db.relationship("Order", backref="payment", lazy=True)