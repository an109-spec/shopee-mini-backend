import os
import uuid
from datetime import datetime
from decimal import Decimal

from flask import (
    render_template,
    request,
    redirect,
    session,
    jsonify,
    url_for,
    flash,
    current_app,
)
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import User, Shop, Product, Category
from app.common.security.permission import seller_required
from app.common.exceptions import ForbiddenError, ValidationError, AppException
from app.modules.chat.service import ChatService

from . import seller_bp
from .dto import CreateShopDTO, ShippingSetupDTO
from .service import SellerService
from .center_service import SellerCenterService, ShopUpdateDTO, PromotionCreateDTO
from .product_service import SellerProductService, SellerProductUpdateDTO, SellerProductCreateDTO
from .repository import SellerRepository
import os
from werkzeug.utils import secure_filename

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
    labels = ["Thông tin Shop", "Cài đặt vận chuyển"]

    return [
        {
            "label": label,
            "index": i + 1,
            "active": i + 1 == active_step,
        }
        for i, label in enumerate(labels)
    ]


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
        return redirect(
            url_for(
                "auth.login",
                next=url_for("seller.register_shop"),
                role="seller",
            )
        )

    shop = Shop.query.filter_by(owner_id=user.id).first()

    if shop and shop.shipping_configured:
        return redirect(url_for("seller.seller_center"))

    if request.method == "GET":

        form = {}

        if shop:
            form = {
                "name": shop.name,
                "pickup_address": shop.pickup_address,
                "email": shop.contact_email,
                "phone": shop.contact_phone,
            }

        return render_template(
            "seller/shop/register_shop.html",
            steps=_build_steps(shop),
            form=form,
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
            form=form,
        )

    return redirect(url_for("seller.shipping_setup"))


@seller_bp.route("/shipping_setup", methods=["GET", "POST"])
def shipping_setup():
    user = get_current_user()

    if not user:
        return redirect(
            url_for(
                "auth.login",
                next=url_for("seller.shipping_setup"),
                role="seller",
            )
        )

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
                error=str(e),
            )

        return redirect(url_for("seller.dashboard"))

    return render_template(
        "seller/shop/shipping_setup.html",
        shop=shop,
        steps=_build_steps(shop),
    )


@seller_bp.route("/dashboard")
@seller_required
def dashboard():
    user = get_current_user()
    shop = get_current_shop(user)

    data = SellerCenterService.get_dashboard(shop.id)

    return render_template(
        "seller/dashboard.html",
        shop=shop,
        todo=data["todo"],
        today_revenue=data["today_revenue"],
        total_orders=data["total_orders"],
        total_products=data["total_products"],
        recent_orders=data["recent_orders"],
    )


@seller_bp.route("/products")
@seller_required
def product_list():
    user = get_current_user()
    shop = get_current_shop(user)

    products = SellerProductService.list_products(shop.id)

    return render_template(
        "seller/product/product_list.html",
        products=products,
    )


@seller_bp.route("/products/create", methods=["GET", "POST"])
@seller_required
def create_product():

    user = get_current_user()
    shop = get_current_shop(user)

    categories = Category.query.all()

    if request.method == "GET":
        return render_template(
            "seller/product/product_create.html",
            categories=categories,
            form=None,
            error=None
        )

    try:

        name = request.form.get("name")
        description = request.form.get("description")
        category_id = request.form.get("category_id")

        if not name:
            raise ValueError("Tên sản phẩm không được để trống")

        if not category_id:
            raise ValueError("Phải chọn danh mục")

        prices = request.form.getlist("variant_price[]")
        stocks = request.form.getlist("variant_stock[]")
        sizes = request.form.getlist("variant_size[]")
        colors = request.form.getlist("variant_color[]")
        variant_images = request.files.getlist("variant_image[]")

        count = min(len(prices), len(stocks), len(sizes), len(colors))

        if count == 0:
            raise ValueError("Phải có ít nhất 1 phân loại")

        upload_folder = os.path.join(
            current_app.root_path,
            "static/uploads/products"
        )

        os.makedirs(upload_folder, exist_ok=True)

        variants = []

        for i in range(count):

            price = Decimal(prices[i] or 0)
            stock = int(stocks[i] or 0)
            size = sizes[i]
            color = colors[i]

            image_url = None

            if i < len(variant_images):
                img = variant_images[i]

                if img and img.filename:

                    filename = secure_filename(img.filename)
                    unique = str(uuid.uuid4()) + "_" + filename

                    path = os.path.join(upload_folder, unique)

                    img.save(path)

                    image_url = f"/static/uploads/products/{unique}"

            variants.append({
                "price": price,
                "stock": stock,
                "image": image_url,
                "attributes": {
                    "size": size,
                    "color": color
                }
            })

        # upload product images
        product_images = request.files.getlist("images[]")

        if len(product_images) > 9:
            raise ValueError("Tối đa 9 ảnh sản phẩm")

        images = []

        for file in product_images:

            if file and file.filename:

                filename = secure_filename(file.filename)
                unique = str(uuid.uuid4()) + "_" + filename

                path = os.path.join(upload_folder, unique)

                file.save(path)

                images.append(
                    f"/static/uploads/products/{unique}"
                )

        dto = SellerProductCreateDTO(
            name=name,
            description=description,
            category_id=int(category_id),
            images=images,
            variants=variants
        )

        SellerProductService.create(shop.id, dto)

        return redirect(url_for("seller.product_list"))

    except (TypeError, ValueError) as e:

        return render_template(
            "seller/product/product_create.html",
            categories=categories,
            error=str(e),
            form=request.form
        )

    except AppException as e:

        return render_template(
            "seller/product/product_create.html",
            categories=categories,
            error=str(e),
            form=request.form
        )

@seller_bp.route("/products/<int:pid>/delete")
@seller_required
def delete_product(pid):

    user = get_current_user()
    shop = get_current_shop(user)

    product = Product.query.filter_by(
        id=pid,
        shop_id=shop.id,
    ).first_or_404()

    db.session.delete(product)
    db.session.commit()

    flash("Xóa sản phẩm thành công!", "success")

    return redirect(url_for("seller.product_list"))


@seller_bp.route("/products/<int:pid>/edit", methods=["GET", "POST"])
@seller_required
def edit_product(pid):

    user = get_current_user()
    shop = get_current_shop(user)

    product = SellerRepository.get_product(shop.id, pid)

    if not product:
        raise AppException("Product not found")

    if request.method == "GET":
        return render_template(
            "seller/product/product_edit.html",
            product=product,
            variants=product.variants
        )

    try:

        name = request.form.get("name")
        description = request.form.get("description")

        variants = []

        prices = request.form.getlist("variant_price[]")
        stocks = request.form.getlist("variant_stock[]")
        sizes = request.form.getlist("variant_size[]")
        colors = request.form.getlist("variant_color[]")

        for i in range(len(prices)):

            price = prices[i]
            stock = stocks[i]
            size = sizes[i]
            color = colors[i]

            if not price or not stock:
                continue

            variants.append({
                "price": Decimal(price),
                "stock": int(stock),
                "attributes": {
                    "size": size,
                    "color": color
                }
            })
        if not variants:
            raise Exception("Sản phẩm phải có ít nhất 1 phân loại")
        SellerProductService.update_variants(
            shop.id,
            pid,
            name,
            description,
            variants
        )
        images = request.files.getlist("images")

        if images:

            image_urls = []

            for img in images:

                if img.filename == "":
                    continue

                filename = secure_filename(img.filename)

                save_path = os.path.join(
                    "app/static/uploads",
                    filename
                )

                img.save(save_path)

                image_urls.append(
                    "/static/uploads/" + filename
                )

            SellerRepository.create_product_images(
                pid,
                image_urls
            )

    except Exception as e:

        return render_template(
            "seller/product/product_edit.html",
            product=product,
            variants=product.variants,
            error=str(e),
        )

    return redirect(url_for("seller.product_list"))

@seller_bp.route("/products/<int:pid>/hide")
@seller_required
def hide_product(pid):

    user = get_current_user()
    shop = get_current_shop(user)

    SellerProductService.update_status(shop.id, pid, "HIDDEN")

    return redirect(url_for("seller.product_list"))


@seller_bp.route("/products/<int:pid>/activate")
@seller_required
def activate_product(pid):

    user = get_current_user()
    shop = get_current_shop(user)

    SellerProductService.update_status(shop.id, pid, "ACTIVE")

    return redirect(url_for("seller.product_list"))

@seller_bp.route("/products/<int:pid>/restock", methods=["POST"])
@seller_required
def restock_product(pid):

    user = get_current_user()
    shop = get_current_shop(user)

    quantity = request.form.get("quantity")

    if not quantity:
        flash("Vui lòng nhập số lượng", "error")
        return redirect(url_for("seller.product_list"))

    quantity = int(quantity)

    SellerProductService.restock(shop.id, pid, quantity)

    flash("Nhập kho thành công", "success")

    return redirect(url_for("seller.product_list"))


@seller_bp.route("/orders")
@seller_required
def orders_page():

    user = get_current_user()
    shop = get_current_shop(user)

    status = request.args.get("status")

    orders = SellerCenterService.list_orders(shop.id, status)

    return render_template(
        "seller/order/order_list.html",
        orders=orders,
        status=status or "ALL",
    )


@seller_bp.route("/chat")
@seller_required
def chat_page():

    user = get_current_user()

    rooms = SellerCenterService.get_chat_overview(user.id)

    return render_template(
        "seller/chat.html",
        rooms=rooms,
    )


@seller_bp.route("/shipping")
@seller_required
def shipping_page():

    user = get_current_user()
    shop = get_current_shop(user)

    return render_template(
        "seller/shipping.html",
        shop=shop,
    )


@seller_bp.route("/promotions")
@seller_required
def promotions_page():

    user = get_current_user()
    shop = get_current_shop(user)

    products = SellerRepository.list_products(shop.id)
    promotions = SellerRepository.list_flash_sales_for_shop(shop.id)

    return render_template(
        "seller/promotions.html",
        products=products,
        promotions=promotions,
    )


@seller_bp.route("/revenue")
@seller_required
def revenue_page():

    user = get_current_user()
    shop = get_current_shop(user)

    summary = SellerCenterService.get_revenue_summary(shop.id)

    return render_template(
        "seller/revenue.html",
        summary=summary,
    )


@seller_bp.route("/shop-settings")
@seller_required
def shop_settings_page():

    user = get_current_user()
    shop = get_current_shop(user)

    return render_template(
        "seller/shop/settings.html",
        shop=shop,
    )


@seller_bp.route("/become")
def become_seller():

    user = get_current_user()

    if not user:
        return redirect(
            url_for(
                "auth.login",
                next=url_for("seller.register_shop"),
                role="seller",
            )
        )

    if user.is_seller:
        return redirect(url_for("seller.seller_center"))

    return redirect(url_for("seller.register_shop"))