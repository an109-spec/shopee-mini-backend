from flask import render_template, request, redirect, session, jsonify, url_for

from app.models import User, Shop

from . import seller_bp
from .service import SellerService
from .product_manager import ProductManager
from .dto import (
    CreateProductDTO,
    CreateShopDTO,
    ShippingSetupDTO
)

from app.common.security.permission import seller_required
from app.common.exceptions import ForbiddenError, ValidationError

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


def _build_steps(shop):
    active_step = shop.onboarding_step if shop else 1
    labels = [
        "Thông tin Shop",
        "Cài đặt vận chuyển"
    ]
    return [{"label": label, "index": i + 1, "active": i + 1 == active_step} for i, label in enumerate(labels)]

@seller_bp.route("/")
def seller_center():

    user = get_current_user()

    if not user:
        return redirect(url_for("auth.login", next="/seller", role="seller"))

    shop = Shop.query.filter_by(owner_id=user.id).first()

    if not shop:
        return redirect(url_for("seller.register_shop"))

    if not shop.shipping_configured:
        return redirect(url_for("seller.shipping_setup"))

    return redirect(url_for("seller.dashboard"))


@seller_bp.route("/register_shop", methods=["GET", "POST"])
def register_shop():

    user = get_current_user()

    if not user:
        return redirect(url_for("auth.login",
            next=url_for("seller.register_shop"),
            role="seller"
        ))

    shop = Shop.query.filter_by(owner_id=user.id).first()

    if shop and shop.shipping_configured:
        return redirect(url_for("seller.seller_center"))

    if request.method == "GET":

        form = {}

        if shop:
            form = {
                "name": shop.name,
                "pickup_address": shop.pickup_address,
                "email": shop.email,
                "phone": shop.phone
            }

        return render_template(
            "seller/shop/register_shop.html",
            steps=_build_steps(shop),
            form=form
        )

    form = {
        "name": (request.form.get("name") or "").strip(),
        "pickup_address": (request.form.get("pickup_address") or "").strip(),
        "email": (request.form.get("email") or "").strip(),
        "phone": (request.form.get("phone") or "").strip(),
    }

    try:
        dto = CreateShopDTO(**form)

        if shop:
            SellerService.update_shop(shop, dto)
        else:
            SellerService.register_shop(user, dto)

    except ValidationError as e:

        return render_template(
            "seller/shop/register_shop.html",
            steps=_build_steps(shop),
            error=str(e),
            form=form
        )

    return redirect(url_for("seller.shipping_setup"))

@seller_bp.route("/shipping_setup", methods=["GET", "POST"])
def shipping_setup():

    user = get_current_user()

    if not user:
        return redirect(url_for("auth.login",
            next=url_for("seller.shipping_setup"),
            role="seller"
        ))

    shop = Shop.query.filter_by(owner_id=user.id).first()

    if not shop:
        return redirect(url_for("seller.register_shop"))

    if request.method == "POST":

        try:
            dto = ShippingSetupDTO(
                fast=request.form.get("hoa_toc") == "on",
                same_day=request.form.get("trong_ngay") == "on",
                express=request.form.get("nhanh") == "on",
                self_delivery=request.form.get("tu_nhan") == "on",
                pickup_point=request.form.get("pickup_point") == "on",
                bulky=request.form.get("cong_kenh") == "on",
            )

            SellerService.setup_shipping(shop, dto)

        except ValidationError as e:
            return render_template(
                "seller/shop/shipping_setup.html",
                shop=shop,
                steps=_build_steps(shop),
                error=str(e)
            )

        return redirect(url_for("seller.dashboard"))

    return render_template(
        "seller/shop/shipping_setup.html",
        shop=shop,
        steps=_build_steps(shop)
    )

@seller_bp.route("/complete")
def complete():
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login", next=url_for("seller.complete"), role="seller"))

    shop = Shop.query.filter_by(owner_id=user.id).first()
    if not shop:
        return redirect(url_for("seller.register_shop"))

    return render_template("seller/shop/complete.html", shop=shop, steps=_build_steps(shop))

@seller_bp.route("/dashboard")
@seller_required
def dashboard():

    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login", role="seller"))
    shop = get_current_shop(user)

    products = ProductManager.get_products(shop.id)

    return render_template(
        "seller/dashboard.html",
        shop=shop,
        products=products
    )

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

@seller_bp.route("/products/<int:pid>/delete")
@seller_required
def delete_product(pid):

    ProductManager.delete(pid)

    return redirect("/seller/products")

@seller_bp.route("/api/revenue")
@seller_required
def revenue_api():

    data = {
        "labels": ["T2", "T3", "T4", "T5", "T6", "T7", "CN"],
        "values": [200, 350, 150, 400, 500, 300, 600]
    }

    return jsonify(data)
@seller_bp.route("/become")
def become_seller():

    user = get_current_user()

    if not user:
        return redirect(url_for("auth.login", next=url_for("seller.register_shop"), role="seller"))

    if user.is_seller:
        return redirect(url_for("seller.seller_center"))

    return redirect(url_for("seller.register_shop"))