from dataclasses import dataclass
from decimal import Decimal
import re

from app.common.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.core.enums.product_status import ProductStatus
from app.models import Product

from .repository import SellerRepository


@dataclass
class SellerProductCreateDTO:
    name: str
    description: str | None
    price: Decimal
    stock: int
    category_id: int | None
    images: list[str]


@dataclass
class SellerProductUpdateDTO:
    product_id: int
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock: int | None = None
    category_id: int | None = None


class SellerProductService:
    @staticmethod
    def _slugify(name: str) -> str:
        base = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
        return base or "product"

    @staticmethod
    def _validate_price(price: Decimal):
        if price <= 0:
            raise ValidationError("Giá sản phẩm phải lớn hơn 0")

    @staticmethod
    def _validate_stock(stock: int):
        if stock < 0:
            raise ValidationError("Tồn kho không được âm")

    @staticmethod
    def _check_ownership(product: Product, shop_id: int):
        if product.shop_id != shop_id:
            raise ForbiddenError("Bạn không có quyền thao tác sản phẩm này")

    @staticmethod
    def create(shop_id: int, dto: SellerProductCreateDTO):
        if not dto.name or len(dto.name.strip()) < 3:
            raise ValidationError("Tên sản phẩm tối thiểu 3 ký tự")
        SellerProductService._validate_price(dto.price)
        SellerProductService._validate_stock(dto.stock)

        slug_base = SellerProductService._slugify(dto.name)
        slug = slug_base
        idx = 1
        while Product.query.filter_by(slug=slug).first():
            idx += 1
            slug = f"{slug_base}-{idx}"

        product = Product(
            shop_id=shop_id,
            name=dto.name.strip(),
            slug=slug,
            description=dto.description,
            price=dto.price,
            stock_quantity=dto.stock,
            category_id=dto.category_id,
            thumbnail=dto.images[0] if dto.images else None,
            status=ProductStatus.ACTIVE,
        )
        SellerRepository.create_product(product)
        if dto.images:
            SellerRepository.create_product_images(product.id, dto.images)
        SellerRepository.commit()

        return {
            "id": product.id,
            "name": product.name,
            "status": product.status.value,
            "index_updated": True,
        }

    @staticmethod
    def list_products(shop_id: int):
        products = SellerRepository.list_products(shop_id)
        return [
            {
                "id": p.id,
                "name": p.name,
                "price": float(p.price),
                "stock": p.stock_quantity,
                "status": p.status.value,
            }
            for p in products
        ]

    @staticmethod
    def update(shop_id: int, dto: SellerProductUpdateDTO):
        product = SellerRepository.get_product(dto.product_id)
        if not product or product.status == ProductStatus.DELETED:
            raise NotFoundError("Không tìm thấy sản phẩm")
        SellerProductService._check_ownership(product, shop_id)

        if dto.name is not None:
            product.name = dto.name.strip()
        if dto.description is not None:
            product.description = dto.description
        if dto.price is not None:
            SellerProductService._validate_price(dto.price)
            product.price = dto.price
        if dto.stock is not None:
            SellerProductService._validate_stock(dto.stock)
            product.stock_quantity = dto.stock
        if dto.category_id is not None:
            product.category_id = dto.category_id

        SellerRepository.commit()
        return {"id": product.id, "updated": True}

    @staticmethod
    def update_stock(shop_id: int, product_id: int, stock: int):
        SellerProductService._validate_stock(stock)
        product = SellerRepository.get_product(product_id)
        if not product or product.status == ProductStatus.DELETED:
            raise NotFoundError("Không tìm thấy sản phẩm")
        SellerProductService._check_ownership(product, shop_id)

        product.stock_quantity = stock
        SellerRepository.commit()
        return {"id": product.id, "stock": product.stock_quantity}

    @staticmethod
    def update_status(shop_id: int, product_id: int, status: str):
        if status not in {ProductStatus.ACTIVE.value, ProductStatus.HIDDEN.value, ProductStatus.DELETED.value}:
            raise ValidationError("Trạng thái không hợp lệ")

        product = SellerRepository.get_product(product_id)
        if not product:
            raise NotFoundError("Không tìm thấy sản phẩm")
        SellerProductService._check_ownership(product, shop_id)

        product.status = ProductStatus(status)
        SellerRepository.commit()
        return {"id": product.id, "status": product.status.value}

    @staticmethod
    def soft_delete(shop_id: int, product_id: int):
        return SellerProductService.update_status(shop_id, product_id, ProductStatus.DELETED.value)