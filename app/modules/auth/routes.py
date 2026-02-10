from flask import request, render_template, redirect, url_for

from . import auth_bp
from .validators import validate_login, validate_register
from .dto import LoginDTO, RegisterDTO
from .service import AuthService


# =========================
# REGISTER
# =========================
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    data = request.form.to_dict()

    errors = validate_register(data)
    if errors:
        return render_template("auth/register.html", errors=errors)

    dto = RegisterDTO(
        email=data["email"],
        password=data["password"],
        full_name=data["full_name"],
    )

    AuthService.register(dto)
    return redirect(url_for("auth.login"))


# =========================
# LOGIN
# =========================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    data = request.form.to_dict()

    errors = validate_login(data)
    if errors:
        return render_template("auth/login.html", error=errors[0])

    dto = LoginDTO(
        email=data["email"],
        password=data["password"]
    )

    AuthService.login(dto)
    return redirect("/")


# =========================
# FORGOT PASSWORD
# =========================
@auth_bp.route("/forgot-password", methods=["GET"])
def forgot_password():
    return render_template("auth/forgot_password.html")
