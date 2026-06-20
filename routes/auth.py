from flask import Blueprint, render_template, request, redirect, url_for
from models import User
from db import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user

auth = Blueprint("auth", __name__)


# ==========================
# REGISTER
# ==========================
@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"))

        # Get location from hidden inputs
        lat = request.form.get("lat")
        lon = request.form.get("lon")

        # Convert to float if exists
        lat = float(lat) if lat else None
        lon = float(lon) if lon else None

        user = User(
            username=username,
            email=email,
            password=password,
            lat=lat,
            lon=lon
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ==========================
# LOGIN
# ==========================
@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user = User.query.filter_by(email=request.form.get("email")).first()

        if user and check_password_hash(user.password, request.form.get("password")):
            login_user(user)
            return redirect(url_for("main.welcome"))

    return render_template("login.html")


# ==========================
# LOGOUT
# ==========================
@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))