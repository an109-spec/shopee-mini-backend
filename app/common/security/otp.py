import secrets
import string
from datetime import datetime, timezone, timedelta

OTP_EXPIRE_MINUTES = 5
def generate_otp(length: int = 6) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(length))

def get_otp_expired_at() -> datetime:
    """Return the expiration time of an OTP (UTC)."""
    now = datetime.now(timezone.utc)
    return now + timedelta(minutes=OTP_EXPIRE_MINUTES)

def is_otp_expired(expired_at: datetime) -> bool:
    return datetime.now(timezone.utc) > expired_at

