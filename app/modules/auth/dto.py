from dataclasses import dataclass


@dataclass
class LoginDTO:
    email: str
    password: str


@dataclass
class RegisterDTO:
    email: str
    password: str
    full_name: str
