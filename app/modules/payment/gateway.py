import uuid


def generate_qr_payment(order):

    transaction_code = uuid.uuid4().hex[:12]

    qr_url = (
        "https://api.qrserver.com/v1/create-qr-code/"
        f"?size=250x250&data=ORDER-{order.id}"
    )

    return {
        "transaction_code": transaction_code,
        "qr_url": qr_url
    }


def verify_mock_callback():
    return True