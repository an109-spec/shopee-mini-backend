from datetime import datetime, timezone
from app.extensions.db import db


class Wishlist(db.Model):
    __tablename__ = "wishlists"

    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    product_id = db.Column(
        db.BigInteger,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
