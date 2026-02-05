from app.extensions.db import db
from .base import BaseModel


class Voucher(BaseModel):
    __tablename__ = "vouchers"

    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_type = db.Column(
        db.Enum("PERCENT", "FIXED", name="discount_type"),
        nullable=False
    )
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)
    used_quantity = db.Column(db.Integer, default=0)

    min_order_amount = db.Column(db.Numeric(12, 2), default=0)
    max_discount = db.Column(db.Numeric(12, 2))
    expired_at = db.Column(db.DateTime, nullable=False)
