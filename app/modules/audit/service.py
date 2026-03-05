from app.models.audit_log import AuditLog
from app.extensions.db import db


class AuditService:

    @staticmethod
    def log(user_id, action, target=None):

        log = AuditLog(
            user_id=user_id,
            action=action,
            target=target
        )

        db.session.add(log)
        db.session.commit()