from app.extensions.db import db
from .base import BaseModel


class OTPCode(BaseModel):
    __tablename__ = "otp_codes"

    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    otp_code = db.Column(db.String(10), nullable=False)
    type = db.Column(db.Enum("email", "sms", name="otp_type"), nullable=False)
    expired_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)


