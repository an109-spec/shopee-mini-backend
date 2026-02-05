from app.extensions.db import db
from .base import BaseModel


class Review(BaseModel):
    __tablename__ = "reviews"

    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id"))
    rating = db.Column(db.SmallInteger, nullable=False)
    comment = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint("user_id", "product_id", name="uq_user_product_review"),
    )



