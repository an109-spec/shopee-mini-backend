from app.extensions.db import db
from .base import BaseModel


class Promotion(BaseModel):
    __tablename__ = "promotions"

    name = db.Column(db.String(200), nullable=False)

    variant_id = db.Column(
        db.BigInteger,
        db.ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False
    )

    discount_percent = db.Column(db.Integer, nullable=False)

    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    end_time = db.Column(db.DateTime(timezone=True), nullable=False)

    is_active = db.Column(db.Boolean, default=True)

    variant = db.relationship(
        "app.models.product.ProductVariant",
        backref="promotions"
    )