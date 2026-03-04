from app.extensions.db import db 
from .base import BaseModel
from datetime import datetime, timezone
class ProductCategory(db.Model):
    __tablename__ = "product_categories"
    
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id"), primary_key=True)
    category_id = db.Column(db.BigInteger, db.ForeignKey("categories.id"), primary_key=True)

    is_primary = db.Column(db.Boolean, default=False)

    product = db.relationship("app.models.product.Product", back_populates="product_categories")
    category = db.relationship("app.models.product.Category", back_populates="product_categories")
class Product(BaseModel):
    __tablename__ = "products"

    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.BigInteger, db.ForeignKey("categories.id"), nullable=True, index=True)
    thumbnail = db.Column(db.String(500), nullable=True)
    qr_code = db.Column(db.String(250))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    shop_id = db.Column(db.BigInteger, db.ForeignKey("shops.id"), nullable=True)
    product_categories = db.relationship(
        "app.models.product.ProductCategory",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    images = db.relationship(
        "app.models.product.ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    reviews = db.relationship(
        "app.models.review.Review",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Category(BaseModel):
    __tablename__ = "categories"

    name = db.Column(db.String(100), nullable=False, unique=True)
    parent_id = db.Column(db.BigInteger, db.ForeignKey("categories.id"))

    parent = db.relationship("app.models.product.Category", remote_side="Category.id", backref="children")
    product_categories = db.relationship(
        "app.models.product.ProductCategory",
        back_populates="category",
        cascade="all, delete-orphan",
    )

class ProductImage(BaseModel):
    __tablename__ = "product_images"

    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)

    product = db.relationship("app.models.product.Product", back_populates="images")
