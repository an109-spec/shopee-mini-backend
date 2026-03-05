from decimal import Decimal
from flask import session
from app.models.product import Product
from .calculator import (
    calculate_subtotal,
    calculate_discount,
    calculate_total,
)


class CartService:

    SESSION_KEY = "cart"

    # =========================
    # GET CART
    # =========================

    @staticmethod
    def get_cart():
        cart = session.get(CartService.SESSION_KEY)

        if not cart:
            cart = {"items": {}}
            session[CartService.SESSION_KEY] = cart

        return cart

    # =========================
    # ADD
    # =========================

    @staticmethod
    def add_to_cart(product_id: int, quantity: int):

        product = Product.query.get(product_id)

        if not product:
            raise ValueError("Product not found")

        if product.stock_quantity < quantity:
            raise ValueError("Insufficient stock")

        cart = CartService.get_cart()
        items = cart["items"]

        product_key = str(product_id)

        if product_key in items:
            new_qty = items[product_key]["quantity"] + quantity

            if new_qty > product.stock_quantity:
                raise ValueError("Exceeds available stock")

            items[product_key]["quantity"] = new_qty
        else:
            items[product_key] = {
                "product_id": product.id,
                "name": product.name,
                "price": str(product.price),
                "quantity": quantity,
                "thumbnail": product.thumbnail,
            }

        session.modified = True

    # =========================
    # REMOVE
    # =========================

    @staticmethod
    def remove_item(product_id: int):
        cart = CartService.get_cart()
        items = cart["items"]

        product_key = str(product_id)

        if product_key in items:
            del items[product_key]

        session.modified = True

    # =========================
    # UPDATE
    # =========================

    @staticmethod
    def update_quantity(product_id: int, quantity: int):

        if quantity <= 0:
            CartService.remove_item(product_id)
            return

        product = Product.query.get(product_id)

        if not product:
            raise ValueError("Product not found")

        if quantity > product.stock_quantity:
            raise ValueError("Exceeds available stock")

        cart = CartService.get_cart()
        items = cart["items"]

        product_key = str(product_id)

        if product_key not in items:
            raise ValueError("Item not in cart")

        items[product_key]["quantity"] = quantity
        session.modified = True

    # =========================
    # CLEAR
    # =========================

    @staticmethod
    def clear_cart():
        session.pop(CartService.SESSION_KEY, None)

    # =========================
    # SUMMARY
    # =========================

    @staticmethod
    def get_summary():

        cart = CartService.get_cart()
        items = cart["items"]

        subtotal = calculate_subtotal(items)
        discount = calculate_discount(subtotal)
        total = calculate_total(subtotal, discount)

        return {
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
            "items_count": sum(i["quantity"] for i in items.values())
        }