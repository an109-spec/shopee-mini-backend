from app.extensions.db import db
from .base import BaseModel


class FlashSale(BaseModel):
    __tablename__ = "flash_sales"

    product_id = db.Column(
        db.BigInteger,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    discount_price = db.Column(db.Numeric(12, 2), nullable=False)

    stock_limit = db.Column(db.Integer, default=0)
    sold_count = db.Column(db.Integer, default=0)

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    is_active = db.Column(db.Boolean, default=True)
