from datetime import datetime, timezone

from app.extensions.db import db


class Product(db.Model):
    __tablename__ = "phase1_products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.Integer, nullable=True, index=True)
    thumbnail = db.Column(db.String(500), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ProductImage(db.Model):
    __tablename__ = "phase1_product_images"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("phase1_products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_url = db.Column(db.String(500), nullable=False)


class Review(db.Model):
    __tablename__ = "phase1_reviews"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("phase1_products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(db.Integer, nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_phase1_review_rating"),
    )


Product.images = db.relationship(
    ProductImage,
    backref="product",
    cascade="all, delete-orphan",
    lazy="selectin",
)
Product.reviews = db.relationship(
    Review,
    backref="product",
    cascade="all, delete-orphan",
    lazy="selectin",
)
