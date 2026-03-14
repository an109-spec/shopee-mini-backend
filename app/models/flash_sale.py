from app.extensions.db import db
from .base import BaseModel
from datetime import datetime, timezone

class FlashSale(BaseModel):
    __tablename__ = "flash_sales"

    variant_id = db.Column(
    db.BigInteger,
    db.ForeignKey("product_variants.id", ondelete="CASCADE"),
    nullable=False
)
    discount_percent = db.Column(db.Integer, nullable=False)

    stock_limit = db.Column(db.Integer, nullable=False)
    sold_count = db.Column(db.Integer, default=0)

    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    end_time = db.Column(db.DateTime(timezone=True), nullable=False)

    is_active = db.Column(db.Boolean, default=True)
    variant = db.relationship("ProductVariant")
    @property
    def flash_price(self):
        return int(
            self.variant.price * (100 - self.discount_percent) / 100
        )
    @property
    def is_running(self):
        now = datetime.now(timezone.utc)

        return (
            self.is_active
            and self.start_time <= now
            and now <= self.end_time
            and self.sold_count < self.stock_limit
        )