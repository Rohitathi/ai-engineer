from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from db import db
from models import Post, User
import math

# ✅ Blueprint MUST be defined first
main = Blueprint("main", __name__)


@main.route("/")
def index():
    return redirect(url_for("auth.login"))


@main.route("/welcome", methods=["GET", "POST"])
@login_required
def welcome():
    if request.method == "POST":
        command = (request.form.get("command") or "").strip().lower()
        if command:
            if "near" in command:
                return redirect(url_for("main.nearby"))
            if "inbox" in command:
                return redirect(url_for("messages.inbox"))
            return redirect(url_for("main.welcome"))

        msg = (request.form.get("message") or "").strip()
        category = (request.form.get("category") or "").strip() or None
        lat = request.form.get("lat")
        lon = request.form.get("lon")

        if msg:
            post = Post(
                message=msg,
                category=category,
                user_id=current_user.id,
                lat=float(lat) if lat else None,
                lon=float(lon) if lon else None
            )
            db.session.add(post)

            if lat and lon:
                current_user.lat = float(lat)
                current_user.lon = float(lon)

            db.session.commit()
            return redirect(url_for("main.welcome"))

    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("welcome.html", posts=posts)


@main.route("/nearby")
@login_required
def nearby():
    users = User.query.filter(User.id != current_user.id).all()

    nearby_users = []

    for user in users:
        if (
            user.lat is not None and
            user.lon is not None and
            current_user.lat is not None and
            current_user.lon is not None
        ):
            distance = math.sqrt(
                (current_user.lat - user.lat) ** 2 +
                (current_user.lon - user.lon) ** 2
            )

            if distance < 1:
                nearby_users.append(user)

    return render_template("nearby.html", users=nearby_users)
