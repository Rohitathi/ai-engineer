from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from db import db
from models import Message, User
from connect_ai.agent.agent import ConnectAgent

messages = Blueprint("messages", __name__)

agent = ConnectAgent()


# ==========================
# MESSAGE PAGE
# ==========================
@messages.route("/message/<int:user_id>", methods=["GET", "POST"])
@login_required
def message(user_id):

    other_user = User.query.get_or_404(user_id)

    if request.method == "POST":

        content = request.form.get("content")

        if content:

            text = content.lower().strip()

            # open inbox command
            if "inbox" in text:
                return redirect(url_for("messages.inbox"))

            # AI command
            elif agent.should_handle(content):
                result = agent.run(content)
                ai_reply = result.get("reply", "AI could not process request.")

                msg = Message(
                    sender_id=current_user.id,
                    receiver_id=user_id,
                    content="AI: " + ai_reply
                )

            else:
                msg = Message(
                    sender_id=current_user.id,
                    receiver_id=user_id,
                    content=content
                )

            db.session.add(msg)
            db.session.commit()

        return redirect(url_for("messages.message", user_id=user_id))

    conversation = Message.query.filter(
        ((Message.sender_id == current_user.id) &
         (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) &
         (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()

    return render_template(
        "message.html",
        conversation=conversation,
        other_user=other_user
    )


# ==========================
# INBOX PAGE
# ==========================
@messages.route("/inbox")
@login_required
def inbox():

    messages_received = Message.query.filter_by(
        receiver_id=current_user.id
    ).order_by(Message.created_at.desc()).all()

    unique_users = {}

    for msg in messages_received:
        if msg.sender_id not in unique_users:
            unique_users[msg.sender_id] = msg.sender

    return render_template(
        "inbox.html",
        users=unique_users.values()
    )
