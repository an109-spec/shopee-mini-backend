from openpyxl import Workbook
from app.models import Order


def export_all_orders_excel():

    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"

    ws.append(["Order Code", "User ID", "Total", "Status", "Created At"])

    orders = Order.query.all()

    for order in orders:
        ws.append([
            order.order_code,
            order.user_id,
            float(order.total_price),
            order.status,
            order.created_at.isoformat()
        ])

    return wb