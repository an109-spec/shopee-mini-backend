from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy import event

from app.extensions.db import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


@event.listens_for(BaseModel, "before_insert", propagate=True)
def assign_bigint_id(mapper, connection, target):
    if getattr(target, "id", None) is not None:
        return



    max_id = connection.execute(select(func.max(target.__table__.c.id))).scalar()
    target.id = (max_id or 0) + 1