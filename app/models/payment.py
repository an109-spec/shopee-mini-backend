from app.extensions.db import db
from .base import BaseModel


class Payment(BaseModel):
    __tablename__ = "payments"

    order_id = db.Column(db.BigInteger, db.ForeignKey("orders.id"))
    method = db.Column(db.String(30))
    status = db.Column(db.String(30))
    transaction_code = db.Column(db.String(100))
    amount = db.Column(db.Numeric(12, 2))
    provider = db.Column(db.String(50))
    paid_at = db.Column(db.DateTime)
