from flask import jsonify
from . import audit_bp
from app.models.audit_log import AuditLog


@audit_bp.route("/logs")
def logs():

    logs = AuditLog.query.order_by(
        AuditLog.created_at.desc()
    ).limit(100)

    return jsonify([
        {
            "user_id": l.user_id,
            "action": l.action,
            "target": l.target,
            "time": l.created_at
        }
        for l in logs
    ])