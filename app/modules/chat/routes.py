from flask import render_template, jsonify
from flask_login import login_required, current_user
from .service import ChatService
from . import chat_bp

from .service import ChatService



@chat_bp.route("/<int:seller_id>")
@login_required
def open_chat(seller_id):

    room = ChatService.get_or_create_room(
        buyer_id=current_user.id,
        seller_id=seller_id
    )

    return render_template(
        "chat/chat.html",
        room_id=room.id,
        seller_id=seller_id
    )


@chat_bp.route("/history/<int:room_id>")
@login_required
def history(room_id):

    messages = ChatService.get_chat_history(room_id)

    data = [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "content": m.content,
            "image": m.image,
            "created_at": str(m.created_at)
        }
        for m in messages
    ]

    return jsonify(data)