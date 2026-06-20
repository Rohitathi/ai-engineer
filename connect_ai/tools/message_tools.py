from flask_login import current_user
from sqlalchemy import and_, or_

from models import Message


def get_inbox(limit=20):
    messages = (
        Message.query.filter_by(receiver_id=current_user.id).order_by(Message.id.desc()).limit(limit).all()
    )
    return [
        {
            "message_id": message.id,
            "sender": message.sender_id,
            "receiver": message.receiver_id,
            "content": message.content,
        }
        for message in messages
    ]


def get_chat(user_id=None, limit=50):
    query = Message.query
    if user_id:
        query = query.filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
                and_(Message.sender_id == user_id, Message.receiver_id == current_user.id),
            )
        )
    else:
        query = query.filter(
            or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id)
        )

    messages = query.order_by(Message.id.asc()).limit(limit).all()
    return [
        {
            "message_id": message.id,
            "sender": message.sender_id,
            "receiver": message.receiver_id,
            "content": message.content,
        }
        for message in messages
    ]
