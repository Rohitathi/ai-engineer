from werkzeug.security import generate_password_hash

from app import app
from db import db
from models import User


def create_user(email="chatgpt@example.com", password="password123", username="ChatGPT"):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(username=username, email=email, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            print(f"Created user {email}")
        else:
            print(f"User {email} already exists")


def run():
    create_user()

    with app.test_client() as c:
        resp = c.post("/login", data={"email": "chatgpt@example.com", "password": "password123"}, follow_redirects=True)

        if resp.status_code == 200 and b"Welcome" in resp.data:
            print("Login succeeded (followed redirect to welcome).")
        elif resp.status_code in (302, 303) and resp.location:
            print(f"Login redirected to: {resp.location}")
        else:
            print("Login failed. Response status:", resp.status_code)
            print(resp.data.decode(errors="replace")[:400])


if __name__ == "__main__":
    run()
