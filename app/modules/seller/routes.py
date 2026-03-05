from flask import render_template, request, redirect, session, jsonify
from app.models import User, Shop
from app.extensions import db

from . import seller_bp
from .service import SellerService
from .product_manager import ProductManager


def get_current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)


@seller_bp.route("/")
def seller_center():

    user = get_current_user()

    if user.role != "seller":
        return redirect("/seller/register_shop")

    return redirect("/seller/dashboard")


# register shop
@seller_bp.route("/register_shop", methods=["GET","POST"])
def register_shop():

    user = get_current_user()

    if request.method == "GET":
        return render_template("seller/shop/register_shop.html")

    name = request.form.get("name")

    SellerService.register_shop(user, name)

    return redirect("/seller/dashboard")

from app.common.security.permission import seller_required


@seller_bp.route("/dashboard")
@seller_required
def dashboard():
    user = get_current_user()

    shop = Shop.query.filter_by(owner_id=user.id).first()

    products = shop.products

    return render_template(
        "seller/dashboard.html",
        shop=shop,
        products=products
    )


# product list
@seller_bp.route("/products")
def product_list():

    user = get_current_user()

    shop = Shop.query.filter_by(owner_id=user.id).first()

    products = ProductManager.get_products(shop.id)

    return render_template(
        "seller/product/product_list.html",
        products=products
    )


# create product
@seller_bp.route("/products/create", methods=["GET","POST"])
def create_product():

    user = get_current_user()

    shop = Shop.query.filter_by(owner_id=user.id).first()

    if request.method == "GET":
        return render_template("seller/product/product_create.html")

    dto = {
        "name": request.form.get("name"),
        "price": float(request.form.get("price")),
        "stock": int(request.form.get("stock")),
        "description": request.form.get("description")
    }

    ProductManager.create(shop.id, dto)

    return redirect("/seller/products")


# delete product
@seller_bp.route("/products/<int:pid>/delete")
def delete_product(pid):

    ProductManager.delete(pid)

    return redirect("/seller/products")

@seller_bp.route("/api/revenue")
def revenue_api():

    data = {
        "labels": ["T2","T3","T4","T5","T6","T7","CN"],
        "values": [200,350,150,400,500,300,600]
    }

    return jsonify(data)