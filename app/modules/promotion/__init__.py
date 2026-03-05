from flask import Blueprint

promotion_bp = Blueprint(
    "promotion",
    __name__,
    url_prefix="/promotion"
)

from . import routes