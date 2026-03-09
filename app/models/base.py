from datetime import datetime, timezone
from sqlalchemy import func, select, event
from app.extensions.db import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.BigInteger, primary_key=True)

    created_at = db.Column(
        db.DateTime(timezone=True),  # ✅ QUAN TRỌNG
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

