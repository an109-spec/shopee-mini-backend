from flask import jsonify, render_template, request
from pathlib import Path
from uuid import uuid4
from flask import current_app
from flask import jsonify, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from app.common.exceptions import AppException

from . import user_bp
from .service import UserService

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

def _resolve_user_id() -> int:
    user_id = session.get("user_id")
    if user_id:
        return int(user_id)

    user_id = request.args.get("user_id", type=int)
    if user_id is None:
        raise AppException("Vui lòng cung cấp user_id hoặc đăng nhập", status_code=400)
    return user_id

@user_bp.route("/center", methods=["GET"])
def user_center_page():
    initial_user_id = session.get("user_id") or request.args.get("user_id", type=int)
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

        return jsonify({
            "success": True,
            "data": data
        }), 200

    except AppException as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), e.status_code

    except Exception:
        return jsonify({
            "success": False,
            "error": "Internal Server Error"
        }), 500


@user_bp.route("/profile", methods=["PATCH"])
def update_profile():
    try:
        user_id = _resolve_user_id()
        if not request.is_json:
            raise AppException("Request body must be JSON", 400)
        payload = request.get_json()
        if payload is None:
            raise AppException("Invalid JSON body", 400)
        data = UserService.update_profile(user_id, payload)
        return jsonify({
            "success": True,
            "data": data
        }), 200
    except AppException as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), e.status_code
    except Exception:
        return jsonify({
            "success": False,
            "error": "Internal Server Error"
        }), 500

@user_bp.route("/avatar/upload", methods=["POST"])
def upload_avatar():
    try:
        user_id = _resolve_user_id()

        if "avatar" not in request.files:
            raise AppException("Vui lòng chọn ảnh avatar", 400)

        file = request.files["avatar"]

        if not file.filename:
            raise AppException("Tên file không hợp lệ", 400)

        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise AppException("Định dạng ảnh không hỗ trợ", 400)

        safe_name = secure_filename(file.filename)
        filename = f"{uuid4().hex}-{safe_name}"

        upload_dir = Path(current_app.root_path) / "static/uploads/avatars"
        upload_dir.mkdir(parents=True, exist_ok=True)

        save_path = upload_dir / filename
        file.save(save_path)

        avatar_path = url_for("static", filename=f"uploads/avatars/{filename}")
        avatar_url = UserService.set_avatar_file(user_id, avatar_path)

        return jsonify({"avatar": avatar_url}), 200

    except AppException as e:
        return jsonify({"error": str(e)}), e.status_code

    except Exception:
        return jsonify({"error": "Internal Server Error"}), 500

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