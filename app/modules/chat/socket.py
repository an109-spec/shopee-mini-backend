from flask_login import current_user
from flask_socketio import emit, join_room, leave_room

from app.extensions.socketio import socketio
from .service import ChatService


online_users = set()


@socketio.on("connect")
def on_connect():

    if current_user.is_authenticated:
        online_users.add(current_user.id)

        emit(
            "user_online",
            {"user_id": current_user.id},
            broadcast=True
        )


@socketio.on("disconnect")
def on_disconnect():

    if current_user.is_authenticated:

        online_users.discard(current_user.id)

        emit(
            "user_offline",
            {"user_id": current_user.id},
            broadcast=True
        )


@socketio.on("join_room")
def join_chat(data):

    room_id = data["room_id"]

    join_room(f"room_{room_id}")


@socketio.on("typing")
def typing(data):

    emit(
        "user_typing",
        {
            "user_id": current_user.id
        },
        room=f"room_{data['room_id']}",
        include_self=False
    )


@socketio.on("send_message")
def on_message(data):

    room_id = data["room_id"]
    content = data.get("content")

    msg = ChatService.save_message(
        room_id=room_id,
        sender_id=current_user.id,
        content=content
    )

    emit(
        "receive_message",
        {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "content": msg.content,
            "image": msg.image,
            "created_at": str(msg.created_at)
        },
        room=f"room_{room_id}"
    )


@socketio.on("seen")
def mark_seen(data):

    room_id = data["room_id"]

    ChatService.mark_seen(room_id, current_user.id)

    emit(
        "messages_seen",
        {"room_id": room_id},
        room=f"room_{room_id}"
    )