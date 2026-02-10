from flask import request, jsonify

from . import auth_bp
from .validators import validate_login, validate_register
from .dto import LoginDTO, RegisterDTO
from .service import AuthService


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}

    validate_register(data)

    dto = RegisterDTO(
        email=data["email"],
        password=data["password"],
        full_name=data["full_name"],
    )

    user = AuthService.register(dto)

    return jsonify({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}

    validate_login(data)

    dto = LoginDTO(
        email=data["email"],
        password=data["password"]
    )

    user = AuthService.login(dto)

    return jsonify({
        "id": user.id,
        "email": user.email
    })
