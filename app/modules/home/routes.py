from flask import render_template, session

from . import home_bp
from .service import HomeService


@home_bp.route("/", methods=["GET"])
def home_page():
    context = HomeService.build_home_context()
    cart = session.get("cart") or {}
    cart_items = cart.get("items") or {}
    context["cart_count"] = sum(int(item.get("quantity", 0)) for item in cart_items.values())

    return render_template("home/index.html", **context)
@home_bp.route("/support", methods=["GET"])
def support_page():
    return render_template("home/support.html")