from app.extensions.db import db
from .base import BaseModel


class Review(BaseModel):
    __tablename__ = "reviews"

    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = db.Column(db.SmallInteger, nullable=False)
    comment = db.Column(db.Text)
    product = db.relationship("app.models.product.Product", back_populates="reviews")
    __table_args__ = (
        db.UniqueConstraint("user_id", "product_id", name="uq_user_product_review"),
        db.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
    )



