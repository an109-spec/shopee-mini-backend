from app.common.exceptions import ConflictError, NotFoundError
from app.extensions.db import db

from .dto import ProductCreateDTO, ProductResponseDTO, ProductUpdateDTO, ReviewCreateDTO
from .filters import filter_by_category, filter_by_price, sort_products
from app.models.product import Product, ProductImage
from app.core.enums.product_status import ProductStatus
from app.models.review import Review
from .search import full_text_query


class ProductService:
    @staticmethod
    def list_products(*, keyword=None, min_price=None, max_price=None, category=None, sort=None, page=1, per_page=10):
        query = Product.query.filter(Product.status == ProductStatus.ACTIVE)
        query = full_text_query(query, keyword)
        query = filter_by_price(query, min_price, max_price)
        query = filter_by_category(query, category)
        query = sort_products(query, sort)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            "items": [ProductResponseDTO.from_model(item).to_dict() for item in pagination.items],
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
        }

    @staticmethod
    def create_product(data: ProductCreateDTO):
        exists = Product.query.filter_by(slug=data.slug).first()
        if exists:
            raise ConflictError("slug đã tồn tại")

        product = Product(
            name=data.name,
            slug=data.slug,
            description=data.description,
            price=data.price,
            stock_quantity=data.stock_quantity,
            category_id=data.category_id,
            thumbnail=data.thumbnail,
        )
        db.session.add(product)
        db.session.flush()

        if data.thumbnail:
            db.session.add(ProductImage(product_id=product.id, image_url=data.thumbnail))

        db.session.commit()
        return ProductResponseDTO.from_model(product).to_dict()

    @staticmethod
    def update_product(product_id: int, data: ProductUpdateDTO):
        product = Product.query.filter(Product.id == product_id, Product.status != ProductStatus.DELETED).first()
        if not product:
            raise NotFoundError("Không tìm thấy sản phẩm")

        if data.slug is not None and data.slug != product.slug:
            exists = Product.query.filter(Product.slug == data.slug, Product.id != product_id).first()
            if exists:
                raise ConflictError("slug đã tồn tại")
            product.slug = data.slug

        if data.name is not None:
            product.name = data.name
        if data.description is not None:
            product.description = data.description
        if data.price is not None:
            product.price = data.price
        if data.stock_quantity is not None:
            product.stock_quantity = data.stock_quantity
        if data.category_id_provided:
            product.category_id = data.category_id
        if data.thumbnail is not None:
            product.thumbnail = data.thumbnail

        db.session.commit()
        return ProductResponseDTO.from_model(product).to_dict()

    @staticmethod
    def delete_product(product_id: int):
        product = Product.query.filter(Product.id == product_id, Product.status == ProductStatus.ACTIVE).first()
        if not product:
            raise NotFoundError("Không tìm thấy sản phẩm")

        product.status = ProductStatus.DELETED
        db.session.commit()

    @staticmethod
    def get_product_detail(product_id: int):
        product = Product.query.filter(Product.id == product_id, Product.status == ProductStatus.ACTIVE).first()
        if not product:
            raise NotFoundError("Không tìm thấy sản phẩm")

        payload = ProductResponseDTO.from_model(product).to_dict()
        payload["images"] = [img.image_url for img in product.images]
        payload["reviews_count"] = len(product.reviews)
        return payload

    @staticmethod
    def get_related_products(product_id: int):
        product = Product.query.filter(Product.id == product_id, Product.status == ProductStatus.ACTIVE).first()
        if not product:
            raise NotFoundError("Không tìm thấy sản phẩm")

        related_query = Product.query.filter(Product.id != product_id, Product.status == ProductStatus.ACTIVE)
        if product.category_id is not None:
            related_query = related_query.filter(Product.category_id == product.category_id)

        related = related_query.order_by(Product.created_at.desc()).limit(8).all()
        return [ProductResponseDTO.from_model(item).to_dict() for item in related]

    @staticmethod
    def add_review(product_id: int, user_id: int, data: ReviewCreateDTO):
        product = Product.query.filter(Product.id == product_id, Product.status == ProductStatus.ACTIVE).first()
        if not product:
            raise NotFoundError("Không tìm thấy sản phẩm")

        review = Review(
            product_id=product_id,
            user_id=user_id,
            rating=data.rating,
            comment=data.comment,
        )
        db.session.add(review)
        db.session.commit()

        return {
            "id": review.id,
            "product_id": review.product_id,
            "user_id": review.user_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at.isoformat(),
        }

    @staticmethod
    def get_product_reviews(product_id: int):
        product = Product.query.filter(Product.id == product_id, Product.status == ProductStatus.ACTIVE).first()
        if not product:
            raise NotFoundError("Không tìm thấy sản phẩm")

        reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
        return [
            {
                "id": review.id,
                "product_id": review.product_id,
                "user_id": review.user_id,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.isoformat(),
            }
            for review in reviews
        ]
