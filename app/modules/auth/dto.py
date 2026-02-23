from dataclasses import dataclass
from typing import Optional


@dataclass
class LoginDTO:
    identifier: str   # email hoặc phone
    password: str


@dataclass
class RegisterDTO:
    password: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class RequestPasswordResetDTO:
    identifier: str   # email hoặc phone


@dataclass
class ResetPasswordDTO:
    identifier: str   # email hoặc phone
    otp_code: str
    new_password: str
    otp_type: str = "email"   # mặc định email, có thể là "sms"