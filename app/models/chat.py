from app.extensions.db import db
from .base import BaseModel


class ChatRoom(BaseModel):
    __tablename__ = "chat_rooms"

    buyer_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("buyer_id", "seller_id", name="uq_buyer_seller_room"),
    )


class Message(BaseModel):
    __tablename__ = "messages"

    room_id = db.Column(
        db.BigInteger,
        db.ForeignKey("chat_rooms.id", ondelete="CASCADE"),
        nullable=False
    )
    sender_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text)
    image = db.Column(db.String(255))
