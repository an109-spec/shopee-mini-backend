from flask import jsonify, render_template, request

from app.common.exceptions import AppException

from . import user_bp
from .service import UserService


def _resolve_user_id() -> int:
    user_id = request.args.get("user_id", type=int)
    if user_id is None:
        raise AppException("Thiếu user_id", status_code=400)
    return user_id


@user_bp.route("/center", methods=["GET"])
def user_center_page():
    initial_user_id = request.args.get("user_id", type=int)
    return render_template("user/center.html", initial_user_id=initial_user_id)

@user_bp.route("/avatar/auto", methods=["GET", "POST"])
def auto_avatar():
    if request.method == "GET":
        return jsonify(
            {
                "message": "Dùng POST /user/avatar/auto?user_id=<id> để tạo avatar tự động",
                "example": "/user/avatar/auto?user_id=1",
            }
        ), 200

    try:
        user_id = _resolve_user_id()
        avatar_url = UserService.ensure_auto_avatar(user_id)
        return jsonify({"avatar": avatar_url}), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code


@user_bp.route("/profile", methods=["GET"])
def profile():
    try:
        user_id = _resolve_user_id()
        data = UserService.get_profile(user_id)
        return jsonify(data), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code


@user_bp.route("/avatar", methods=["PATCH"])
def change_avatar():
    try:
        user_id = _resolve_user_id()
        payload = request.get_json(silent=True) or {}
        avatar_url = UserService.change_avatar(user_id, payload.get("avatar"))
        return jsonify({"avatar": avatar_url}), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code


@user_bp.route("/password", methods=["PATCH"])
def change_password():
    try:
        user_id = _resolve_user_id()
        payload = request.get_json(silent=True) or {}
        UserService.change_password(
            user_id=user_id,
            current_password=payload.get("current_password"),
            new_password=payload.get("new_password"),
        )
        return jsonify({"message": "Đổi mật khẩu thành công"}), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code


@user_bp.route("/purchase-history", methods=["GET"])
def purchase_history():
    try:
        user_id = _resolve_user_id()
        history = UserService.purchase_history(user_id)
        return jsonify({"orders": history}), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code