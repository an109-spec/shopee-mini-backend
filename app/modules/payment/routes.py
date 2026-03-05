from flask import render_template, request, jsonify
from app.models import Order
from . import payment_bp
from .service import PaymentService


@payment_bp.route("/select/<int:order_id>")
def select_payment(order_id):

    order = Order.query.get_or_404(order_id)

    return render_template(
        "payment/select_payment.html",
        order=order
    )


@payment_bp.route("/create/<int:order_id>")
def create(order_id):

    order = Order.query.get_or_404(order_id)

    qr = PaymentService.create_payment(order)

    if qr:

        return render_template(
            "payment/payment_qr.html",
            order=order,
            qr_url=qr["qr_url"]
        )

    return render_template(
        "payment/payment_success.html",
        order=order
    )


@payment_bp.route("/confirm", methods=["POST"])
def confirm():

    order_id = request.json.get("order_id")

    PaymentService.confirm_payment(order_id)

    return jsonify({"success": True})


@payment_bp.route("/success/<int:order_id>")
def success(order_id):

    order = Order.query.get_or_404(order_id)

    return render_template(
        "payment/payment_success.html",
        order=order
    )