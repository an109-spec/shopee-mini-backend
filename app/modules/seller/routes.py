from flask import render_template, request, redirect, session, jsonify, url_for
from decimal import Decimal
from datetime import datetime

from app.models import User, Shop, Order, OrderItem, Product, Message
from app.core.enums.order_status import OrderStatus
from app.modules.chat.service import ChatService
from . import seller_bp
from .service import SellerService
from .product_manager import ProductManager
from .product_service import SellerProductService
from .repository import SellerRepository

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
        products=products,
        today_revenue=0,
        total_orders=0,
        total_products=len(products),
        rating=shop.rating or 0,
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

    try:
        dto = CreateProductDTO(
            name=request.form.get("name"),
            price=float(request.form.get("price") or 0),
            stock=int(request.form.get("stock") or 0),
            description=request.form.get("description")
        )
    except (TypeError, ValueError):
        return render_template("seller/product/product_create.html", error="Dữ liệu không hợp lệ")

    ProductManager.create(shop.id, dto)

    return redirect("/seller/products")

@seller_bp.route("/products/<int:pid>/delete")
@seller_required
def delete_product(pid):

    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login", role="seller"))
    shop = get_current_shop(user)

    SellerProductService.soft_delete(shop.id, pid)

    return redirect("/seller/products")

@seller_bp.route("/api/revenue")
@seller_required
def revenue_api():

    data = {
        "labels": ["T2", "T3", "T4", "T5", "T6", "T7", "CN"],
        "values": [200, 350, 150, 400, 500, 300, 600]
    }

    return jsonify(data)

@seller_bp.route("/api/orders", methods=["GET"])
@seller_required
def seller_orders_api():
    user = get_current_user()
    shop = get_current_shop(user)

    status = request.args.get("status")
    query = (
        Order.query.join(OrderItem, OrderItem.order_id == Order.id)
        .join(Product, Product.id == OrderItem.product_id)
        .filter(Product.shop_id == shop.id)
        .distinct()
    )
    if status:
        query = query.filter(Order.status == OrderStatus(status.upper()))

    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify({
        "items": [
            {
                "id": o.id,
                "status": o.status.value,
                "total_price": float(o.total_price),
            }
            for o in orders
        ]
    })


@seller_bp.route("/api/orders/<int:order_id>/status", methods=["PUT"])
@seller_required
def update_order_status(order_id):
    user = get_current_user()
    shop = get_current_shop(user)

    payload = request.get_json() or {}
    new_status = OrderStatus((payload.get("status") or "").upper())

    order = (
        Order.query.join(OrderItem, OrderItem.order_id == Order.id)
        .join(Product, Product.id == OrderItem.product_id)
        .filter(Order.id == order_id, Product.shop_id == shop.id)
        .first()
    )
    if not order:
        raise ForbiddenError("Order not found for current shop")

    order.status = new_status
    from app.extensions import db
    db.session.commit()
    return jsonify({"id": order.id, "status": order.status.value})


@seller_bp.route("/api/chat/message", methods=["POST"])
@seller_required
def seller_send_message():
    user = get_current_user()
    payload = request.get_json() or {}
    buyer_id = int(payload.get("buyer_id", 0))
    room = ChatService.get_or_create_room(buyer_id=buyer_id, seller_id=user.id)
    msg = ChatService.save_message(room.id, user.id, content=payload.get("content"), image=payload.get("image"))
    return jsonify({"id": msg.id, "push_notification": True})


@seller_bp.route("/api/shipping", methods=["PUT"])
@seller_required
def seller_shipping_api():
    user = get_current_user()
    shop = get_current_shop(user)
    payload = request.get_json() or {}
    dto = ShippingSetupDTO(
        fast=bool(payload.get("fast")),
        same_day=bool(payload.get("same_day")),
        express=bool(payload.get("express")),
        self_delivery=bool(payload.get("self_delivery")),
        pickup_point=bool(payload.get("pickup_point")),
        bulky=bool(payload.get("bulky")),
    )
    SellerService.setup_shipping(shop, dto)
    return jsonify({"saved": True})


@seller_bp.route("/api/revenue/summary", methods=["GET"])
@seller_required
def seller_revenue_summary():
    user = get_current_user()
    shop = get_current_shop(user)

    delivered_orders = (
        Order.query.join(OrderItem, OrderItem.order_id == Order.id)
        .join(Product, Product.id == OrderItem.product_id)
        .filter(Product.shop_id == shop.id, Order.status == OrderStatus.DELIVERED)
        .distinct()
        .all()
    )
    revenue = sum(Decimal(o.total_price) for o in delivered_orders)
    platform_fee = revenue * Decimal("0.05")
    shipping_cost = revenue * Decimal("0.02")
    profit = revenue - platform_fee - shipping_cost

    return jsonify({
        "orders": len(delivered_orders),
        "revenue": float(revenue),
        "platform_fee": float(platform_fee),
        "shipping": float(shipping_cost),
        "profit": float(profit),
        "formula": "profit = revenue - platform_fee - shipping",
    })


@seller_bp.route("/api/shop", methods=["PUT"])
@seller_required
def update_shop_profile():
    user = get_current_user()
    shop = get_current_shop(user)
    payload = request.get_json() or {}

    shop.name = payload.get("name", shop.name)
    shop.logo = payload.get("logo", shop.logo)
    shop.pickup_address = payload.get("address", shop.pickup_address)
    shop.updated_at = datetime.utcnow()

    from app.extensions import db
    db.session.commit()

    return jsonify({"saved": True, "shop_id": shop.id})


@seller_bp.route("/api/promotions", methods=["POST"])
@seller_required
def create_promotion():
    payload = request.get_json() or {}
    if int(payload.get("discount_percent", 0)) <= 0:
        raise ValidationError("discount_percent phải > 0")
    return jsonify({"created": True, "promotion": payload}), 201

@seller_bp.route("/become")
def become_seller():

    user = get_current_user()

    if not user:
        return redirect(url_for("auth.login", next=url_for("seller.register_shop"), role="seller"))

    if user.is_seller:
        return redirect(url_for("seller.seller_center"))

    return redirect(url_for("seller.register_shop"))