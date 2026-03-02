from flask import request, render_template, redirect, url_for,session
from app.common.exceptions import (
    UnauthorizedError,
    ValidationError,
    ConflictError
)

from . import auth_bp
from .validators import validate_login, validate_register
from .dto import (
    LoginDTO,
    RegisterDTO,
    RequestPasswordResetDTO,
    ResetPasswordDTO
)
from .service import AuthService


# ======================================================
# REGISTER
# ======================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    data = request.form.to_dict()

    errors = validate_register(data)
    if errors:
        return render_template("auth/register.html", errors=errors)

    dto = RegisterDTO(
        email=data.get("email") or None,
        phone=data.get("phone") or None,
        password=data["password"],
        full_name=data["full_name"],
    )

    try:
        AuthService.register(dto)
        return redirect(url_for("auth.login"))
    except ConflictError as e:
        return render_template("auth/register.html", errors=[str(e)])


# ======================================================
# LOGIN
# ======================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    data = request.form.to_dict()

    try:
        validate_login(data)

        dto = LoginDTO(
            identifier=data["identifier"],
            password=data["password"]
        )

        AuthService.login(dto)
        user = AuthService.login(dto)
        session["user_id"] = user.id
        return redirect(url_for("user.user_center_page"))

    except (ValidationError, UnauthorizedError) as e:
        return render_template(
            "auth/login.html",
            error=str(e),
            locked_until=getattr(e, "locked_until", None)
        )


# ======================================================
# FORGOT PASSWORD
# ======================================================

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("auth/forgot_password.html")

    identifier = request.form.get("identifier")

    try:
        dto = RequestPasswordResetDTO(identifier=identifier)
        AuthService.request_password_reset(dto)

        return render_template(
            "auth/forgot_password.html",
            message="Nếu tài khoản tồn tại, mã OTP đã được gửi."
        )

    except ValidationError as e:
        return render_template(
            "auth/forgot_password.html",
            error=str(e)
        )


# ======================================================
# RESET PASSWORD
# ======================================================

@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        return render_template("auth/reset_password.html")

    data = request.form.to_dict()

    try:
        dto = ResetPasswordDTO(
            identifier=data["identifier"],
            otp_code=data["otp_code"],
            new_password=data["new_password"],
            otp_type=data.get("otp_type", "email")
        )

        AuthService.reset_password(dto)
        return redirect(url_for("auth.login"))

    except (UnauthorizedError, ValidationError, ConflictError) as e:
        return render_template(
            "auth/reset_password.html",
            error=str(e)
        )