from werkzeug.security import generate_password_hash, check_password_hash

from app.models import User
from app.extensions import db
from app.common.exceptions import BadRequestError, UnauthorizedError
from .dto import LoginDTO, RegisterDTO


class AuthService:

    @staticmethod
    def register(dto: RegisterDTO) -> User:
        if User.query.filter_by(email=dto.email).first():
            raise BadRequestError("Email đã tồn tại")

        user = User(
            email=dto.email,
            password_hash=generate_password_hash(dto.password),
            full_name=dto.full_name,
        )

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def login(dto: LoginDTO) -> User:
        user = User.query.filter_by(email=dto.email).first()

        if not user or not check_password_hash(user.password_hash, dto.password):
            raise UnauthorizedError("Sai email hoặc mật khẩu")

        return user
