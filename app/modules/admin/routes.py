from flask import jsonify, request
from . import admin_bp

from .dashboard import DashboardService
from .product_manager import ProductManager
from .order_manager import OrderManager
from .user_manager import UserManager
from .analytics import AnalyticsService
from app.common.security.permission import require_role

@admin_bp.route("/dashboard")
@require_role("admin")
def dashboard():

    data = {
        "total_orders": DashboardService.total_orders(),
        "monthly_revenue": DashboardService.monthly_revenue(),
        "new_users": DashboardService.new_users(),
        "top_products": DashboardService.top_5_products()
    }

    return jsonify(data)


@admin_bp.route("/products")
def products():

    products = ProductManager.list_products()

    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "price": p.price
        }
        for p in products
    ])


@admin_bp.route("/product/price", methods=["POST"])
def update_price():

    data = request.json

    ProductManager.update_price(
        data["product_id"],
        data["price"],
        admin_id=1
    )

    return jsonify({"success": True})


@admin_bp.route("/orders")
def orders():

    orders = OrderManager.list_orders()

    return jsonify([
        {
            "id": o.id,
            "status": o.status,
            "total": o.total_price
        }
        for o in orders
    ])


@admin_bp.route("/orders/status", methods=["POST"])
def update_order_status():

    data = request.json

    OrderManager.change_status(
        data["order_id"],
        data["status"],
        admin_id=1
    )

    return jsonify({"success": True})


@admin_bp.route("/users")
def users():

    users = UserManager.list_users()

    return jsonify([
        {
            "id": u.id,
            "name": (
                u.profile.full_name
                if getattr(u, "profile", None) and u.profile.full_name
                else u.username
            ),
            "email": u.email
        }
        for u in users
    ])


@admin_bp.route("/analytics")
def analytics():

    return jsonify(
        AnalyticsService.revenue_by_month()
    )