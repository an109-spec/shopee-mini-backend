from flask import render_template, request, redirect, url_for, jsonify
from .service import CartService
from . import cart_bp
@cart_bp.route("/")
def view_cart():
    cart = CartService.get_cart()
    summary = CartService.get_summary()
    return render_template("cart/cart.html", cart=cart, summary=summary)


@cart_bp.route("/add", methods=["POST"])
def add():
    product_id = int(request.form["product_id"])
    quantity = int(request.form.get("quantity", 1))

    CartService.add_to_cart(product_id, quantity)
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/remove/<int:product_id>", methods=["POST"])
def remove(product_id):
    CartService.remove_item(product_id)
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/update", methods=["POST"])
def update():
    product_id = int(request.form["product_id"])
    quantity = int(request.form["quantity"])

    CartService.update_quantity(product_id, quantity)
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/clear", methods=["POST"])
def clear():
    CartService.clear_cart()
    return redirect(url_for("cart.view_cart"))