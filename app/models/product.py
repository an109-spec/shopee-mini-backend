from app.extensions.db import db 
from .base import BaseModel

class ProductCategory(db.Model):
    __tablename__ = "product_categories"
    
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id"), primary_key=True)
    category_id = db.Column(db.BigInteger, db.ForeignKey("categories.id"), primary_key=True)

    is_primary = db.Column(db.Boolean, default=False)

    product = db.relationship("Product", back_populates="product_categories")
    category = db.relationship("Category", back_populates="product_categories")
class Product(BaseModel):
    __tablename__ = "products"

    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    description=db.Column(db.Text)
    qr_code=db.Column(db.String(250))
    product_categories = db.relationship(
        "ProductCategory",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    shop_id=db.Column(db.BigInteger, db.ForeignKey("shops.id"), nullable=True)
class Category(BaseModel):
    __tablename__ = "categories"

    name = db.Column(db.String(100), nullable=False, unique=True)
    parent_id = db.Column(db.BigInteger, db.ForeignKey("categories.id"))

    parent = db.relationship("Category", remote_side="Category.id", backref="children")
    product_categories = db.relationship(
        "ProductCategory",
        back_populates="category",
        cascade="all, delete-orphan"
    )

class ProductImage(BaseModel):
    __tablename__="product_images"
    product_id=db.Column(db.BigInteger, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    image_url=db.Column(db.String(255), nullable=False)
