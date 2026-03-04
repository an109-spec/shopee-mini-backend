from flask import jsonify, request, send_file, render_template

from app.common.exceptions import AppException, ValidationError

from . import product_bp
from .dto import ProductCreateDTO, ProductUpdateDTO, ReviewCreateDTO
from .service import ProductService
from .qr_service import export_qr_png, generate_product_qr_by_id


@product_bp.route("/shop", methods=["GET"])
def shop_page():
    return render_template("product/list.html")


@product_bp.route("/shop/<int:id>", methods=["GET"])
def shop_detail_page(id: int):
    return render_template("product/detail.html", product_id=id)


@product_bp.route("/shop/search", methods=["GET"])
def shop_search_page():
    return render_template("product/search.html")


def _parse_pagination() -> tuple[int, int]:
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        raise ValidationError("page/per_page phải là số nguyên")

    if page < 1:
        raise ValidationError("page phải >= 1")
    if per_page < 1 or per_page > 100:
        raise ValidationError("per_page phải trong khoảng 1-100")

    return page, per_page


@product_bp.route("/products", methods=["GET"])
def list_products():
    try:
        page, per_page = _parse_pagination()
        result = ProductService.list_products(
            keyword=request.args.get("keyword"),
            min_price=request.args.get("min_price"),
            max_price=request.args.get("max_price"),
            category=request.args.get("category"),
            sort=request.args.get("sort"),
            page=page,
            per_page=per_page,
        )
        return jsonify(result), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code


@product_bp.route("/products/<int:id>", methods=["GET"])
def get_product_detail(id: int):
    try:
        return jsonify(ProductService.get_product_detail(id)), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code


@product_bp.route("/products", methods=["POST"])
def create_product():
    try:
        if not request.is_json:
            raise ValidationError("Request must be JSON")
        dto = ProductCreateDTO.from_dict(request.get_json() or {})
        result = ProductService.create_product(dto)
        return jsonify(result), 201
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code


@product_bp.route("/products/<int:id>", methods=["PUT"])
def update_product(id: int):
    try:
        if not request.is_json:
            raise ValidationError("Request must be JSON")
        dto = ProductUpdateDTO.from_dict(request.get_json() or {})
        result = ProductService.update_product(id, dto)
        return jsonify(result), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code


@product_bp.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id: int):
    try:
        ProductService.delete_product(id)
        return jsonify({"message": "Xóa sản phẩm thành công"}), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code


@product_bp.route("/products/<int:id>/reviews", methods=["GET"])
def get_reviews(id: int):
    try:
        reviews = ProductService.get_product_reviews(id)
        return jsonify({"items": reviews, "total": len(reviews), "page": 1, "per_page": len(reviews)}), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code


@product_bp.route("/products/<int:id>/reviews", methods=["POST"])
def add_review(id: int):
    try:
        if not request.is_json:
            raise ValidationError("Request must be JSON")

        payload = request.get_json() or {}
        fallback_user_id = request.headers.get("X-User-Id")
        dto = ReviewCreateDTO.from_dict(payload, fallback_user_id=fallback_user_id)
        result = ProductService.add_review(id, dto.user_id, dto)
        return jsonify(result), 201
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code


@product_bp.route("/products/<int:id>/related", methods=["GET"])
def related_products(id: int):
    try:
        items = ProductService.get_related_products(id)
        return jsonify({"items": items, "total": len(items), "page": 1, "per_page": len(items)}), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code


@product_bp.route("/products/<int:id>/qr", methods=["GET"])
def get_product_qr(id: int):
    try:
        qr_data = generate_product_qr_by_id(id)
        png_stream = export_qr_png(qr_data)
        return send_file(png_stream, mimetype="image/png")
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code