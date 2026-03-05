from io import BytesIO

from app.common.exceptions import NotFoundError, ValidationError

from app.models.product import Product


def generate_product_qr_by_id(product_id: int):
    product = Product.query.get(product_id)
    if not product:
        raise NotFoundError("Không tìm thấy sản phẩm")
    return {
        "product_id": product.id,
        "slug": product.slug,
    }


def generate_product_qr_by_url(product_url: str):
    return str(product_url)


def export_qr_png(qr_data):
    try:
        import qrcode
    except ModuleNotFoundError as exc:
        raise ValidationError("Thiếu thư viện qrcode") from exc

    qr_img = qrcode.make(str(qr_data))
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer