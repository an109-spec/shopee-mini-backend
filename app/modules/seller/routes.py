from flask import render_template, request, redirect, session, jsonify, url_for

from app.models import User, Shop
from app.extensions import db

from . import seller_bp
from .service import SellerService
from .product_manager import ProductManager
from .dto import CreateProductDTO

from app.common.security.permission import seller_required
from app.common.exceptions import ForbiddenError

def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    return User.query.get(user_id)

def get_current_shop(user):

    shop = Shop.query.filter_by(owner_id=user.id).first()

    if not shop:
        raise ForbiddenError("Shop not found. Please create shop first.")

    return shop


# =========================
# SELLER CENTER
# =========================
@seller_bp.route("/")
def seller_center():

    user = get_current_user()

    if not user:
        return redirect("/auth/login")

    shop = Shop.query.filter_by(owner_id=user.id).first()

    if shop:
        return redirect("/seller/dashboard")

    return redirect("/seller/register_shop")


# =========================
# REGISTER SHOP
# =========================
@seller_bp.route("/register_shop", methods=["GET", "POST"])
def register_shop():

    user = get_current_user()

    if not user:
        return redirect(url_for("auth.login", role="seller"))

    if request.method == "GET":
        return render_template("seller/shop/register_shop.html")

    name = request.form.get("name")

    SellerService.register_shop(user, name)

    return redirect("/seller/dashboard")


# =========================
# DASHBOARD
# =========================
@seller_bp.route("/dashboard")
@seller_required
def dashboard():

    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login", role="seller"))
    shop = get_current_shop(user)

    products = shop.products

    return render_template(
        "seller/dashboard.html",
        shop=shop,
        products=products
    )


# =========================
# PRODUCT LIST
# =========================
@seller_bp.route("/products")
@seller_required
def product_list():

    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login", role="seller"))
    shop = get_current_shop(user)

    products = ProductManager.get_products(shop.id)

    return render_template(
        "seller/product/product_list.html",
        products=products
    )


# =========================
# CREATE PRODUCT
# =========================
@seller_bp.route("/products/create", methods=["GET", "POST"])
@seller_required
def create_product():

    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login", role="seller"))
    shop = get_current_shop(user)

    if request.method == "GET":
        return render_template("seller/product/product_create.html")

    dto = CreateProductDTO(
        name=request.form.get("name"),
        price=float(request.form.get("price")),
        stock=int(request.form.get("stock")),
        description=request.form.get("description")
    )

    ProductManager.create(shop.id, dto)

    return redirect("/seller/products")


# =========================
# DELETE PRODUCT
# =========================
@seller_bp.route("/products/<int:pid>/delete")
@seller_required
def delete_product(pid):

    ProductManager.delete(pid)

    return redirect("/seller/products")


# =========================
# REVENUE API
# =========================
@seller_bp.route("/api/revenue")
@seller_required
def revenue_api():

    data = {
        "labels": ["T2", "T3", "T4", "T5", "T6", "T7", "CN"],
        "values": [200, 350, 150, 400, 500, 300, 600]
    }

    return jsonify(data)