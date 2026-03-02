from pathlib import Path
from uuid import uuid4
from flask import current_app
from flask import jsonify, render_template, request, session, url_for, redirect
from werkzeug.utils import secure_filename

from app.common.exceptions import AppException

from . import user_bp
from .service import UserService

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

def _resolve_user_id() -> int:
    user_id = session.get("user_id")
    if not user_id:
        raise AppException("Bạn chưa đăng nhập", status_code=401)
    return int(user_id)

@user_bp.route("/center", methods=["GET"])
def user_center_page():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    return render_template("user/center.html")


@user_bp.route("/profile", methods=["GET"])
def profile():
    try:
        user_id = _resolve_user_id()
        data = UserService.get_profile(user_id)
        return jsonify(data), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code


@user_bp.route("/profile", methods=["PATCH"])
def update_profile():
    try:
        user_id = _resolve_user_id()
        payload = request.get_json(silent=True) or {}
        data = UserService.update_profile(user_id, payload)
        return jsonify(data), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code
    
@user_bp.route("/avatar/upload", methods=["POST"])
def upload_avatar():
    try:
        user_id = _resolve_user_id()
        file = request.files.get("avatar")
        if file is None or not file.filename:
            raise AppException("Vui lòng chọn ảnh avatar", status_code=400)

        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise AppException("Định dạng ảnh không hỗ trợ", status_code=400)

        safe_name = secure_filename(file.filename)
        filename = f"{uuid4().hex}-{safe_name}"
        upload_dir = Path("app/static/uploads/avatars")
        upload_dir.mkdir(parents=True, exist_ok=True)
        save_path = upload_dir / filename
        file.save(save_path)

        avatar_path = url_for("static", filename=f"uploads/avatars/{filename}")
        avatar_url = UserService.set_avatar_file(user_id, avatar_path)
        return jsonify({"avatar": avatar_url}), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code


@user_bp.route("/avatar", methods=["PATCH"])
def change_avatar():
    try:
        user_id = _resolve_user_id()
        if not request.is_json:
            raise AppException("Request must be JSON", 400)
        payload = request.get_json()
        avatar = payload.get("avatar")
        if not avatar:
            raise AppException("Thiếu avatar URL", 400)
        avatar_url = UserService.change_avatar(user_id, avatar)
        return jsonify({"avatar": avatar_url}), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception:
        return jsonify({"error": "Internal Server Error"}), 500


@user_bp.route("/password", methods=["PATCH"])
def change_password():
    try:
        user_id = _resolve_user_id()
        if not request.is_json:
            raise AppException("Request must be JSON", 400)
        payload = request.get_json()
        current_password = payload.get("current_password")
        new_password = payload.get("new_password")
        if not current_password or not new_password:
            raise AppException("Thiếu thông tin mật khẩu", 400)
        if len(new_password) < 6:
            raise AppException("Mật khẩu mới quá ngắn", 400)
        UserService.change_password(
            user_id=user_id,
            current_password=current_password,
            new_password=new_password,
        )
        return jsonify({"message": "Đổi mật khẩu thành công"}), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception:
        return jsonify({"error": "Internal Server Error"}), 500


@user_bp.route("/purchase-history", methods=["GET"])
def purchase_history():
    try:
        user_id = _resolve_user_id()
        history = UserService.purchase_history(user_id)
        return jsonify({"orders": history}), 200
    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code