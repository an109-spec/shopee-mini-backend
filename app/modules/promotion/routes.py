from flask import jsonify, request
from . import promotion_bp
from .service import PromotionService


@promotion_bp.route("/flash-sales")
def flash_sales():

    sales = PromotionService.get_active_flash_sales()

    return jsonify([
        {
            "product_id": s.product_id,
            "price": s.discount_price
        }
        for s in sales
    ])


@promotion_bp.route("/voucher/validate", methods=["POST"])
def validate_voucher():

    code = request.json["code"]

    voucher = PromotionService.validate_voucher(code)

    if not voucher:
        return jsonify({"valid": False})

    return jsonify({
        "valid": True,
        "discount": float(voucher.discount_value)
    })