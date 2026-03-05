# modules/order/routes.py

from flask import Blueprint, render_template, redirect, url_for, request, session
from .service import OrderService

order_bp = Blueprint("order", __name__, url_prefix="/order")


# ================= USER =================

def require_login():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return user_id


@order_bp.route("/")
def user_order_list():
    user_id = require_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    orders = OrderService.get_user_orders(user_id)
    return render_template(
        "order/user/order_list.html",
        orders=orders
    )


@order_bp.route("/<int:order_id>")
def user_order_detail(order_id):
    user_id = require_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    order = OrderService.get_order_detail(order_id, user_id)
    timeline = OrderService.build_timeline(order)

    return render_template(
        "order/user/order_detail.html",
        order=order,
        timeline=timeline
    )


@order_bp.route("/tracking/<order_code>")
def tracking(order_code):
    data = OrderService.track_by_order_code(order_code)
    return render_template(
        "order/user/tracking.html",
        tracking=data
    )


# ================= ADMIN =================

@order_bp.route("/admin")
def admin_order_list():
    user_id = require_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    # Nếu có role admin thì check thêm ở đây
    orders = OrderService.get_all_orders()
    return render_template(
        "order/admin/admin_order_list.html",
        orders=orders
    )


@order_bp.route("/admin/<int:order_id>")
def admin_order_detail(order_id):
    user_id = require_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    order = OrderService.get_order_detail_admin(order_id)
    timeline = OrderService.build_timeline(order)

    return render_template(
        "order/admin/admin_order_detail.html",
        order=order,
        timeline=timeline
    )


@order_bp.route("/admin/<int:order_id>/update", methods=["POST"])
def admin_update_status(order_id):
    user_id = require_login()
    if not user_id:
        return redirect(url_for("auth.login"))

    new_status = request.form.get("status")
    OrderService.update_status(order_id, new_status)

    return redirect(url_for("order.admin_order_detail", order_id=order_id))