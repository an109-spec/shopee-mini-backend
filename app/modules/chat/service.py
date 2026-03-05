from sqlalchemy import or_, and_

from app.extensions.db import db
from app.models.chat import Message, ChatRoom


class ChatService:

    @staticmethod
    def get_or_create_room(buyer_id, seller_id):

        room = ChatRoom.query.filter_by(
            buyer_id=buyer_id,
            seller_id=seller_id
        ).first()

        if not room:

            room = ChatRoom(
                buyer_id=buyer_id,
                seller_id=seller_id
            )

            db.session.add(room)
            db.session.commit()

        return room


    @staticmethod
    def save_message(room_id, sender_id, content=None, image=None):

        msg = Message(
            room_id=room_id,
            sender_id=sender_id,
            content=content,
            image=image
        )

        db.session.add(msg)
        db.session.commit()

        return msg


    @staticmethod
    def get_chat_history(room_id, limit=50):

        return (
            Message.query
            .filter_by(room_id=room_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .all()
        )


    @staticmethod
    def mark_seen(room_id, user_id):

        messages = (
            Message.query
            .filter(
                Message.room_id == room_id,
                Message.sender_id != user_id,
                Message.seen == False
            )
            .all()
        )

        for m in messages:
            m.seen = True

        db.session.commit()


    @staticmethod
    def get_unread_count(user_id):

        rooms = ChatRoom.query.filter(
            or_(
                ChatRoom.buyer_id == user_id,
                ChatRoom.seller_id == user_id
            )
        ).all()

        room_ids = [r.id for r in rooms]

        return (
            Message.query
            .filter(
                Message.room_id.in_(room_ids),
                Message.sender_id != user_id,
                Message.seen == False
            )
            .count()
        )