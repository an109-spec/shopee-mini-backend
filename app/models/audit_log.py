from app.extensions.db import db
from .base import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    action = db.Column(db.String(100), nullable=False)
    target = db.Column(db.String(100))
