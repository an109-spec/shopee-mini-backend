from app.core.enums.order_status import PaymentMethod


class CODPayment:

    name = PaymentMethod.COD

    @staticmethod
    def process(order):
        return {
            "status": "PENDING",
            "redirect": f"/payment/success/{order.id}"
        }


class MockVNPayPayment:

    name = PaymentMethod.VNPAY

    @staticmethod
    def process(order):
        return {
            "status": "PENDING",
            "redirect": f"/payment/qr/{order.id}"
        }