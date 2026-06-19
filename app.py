from flask import Flask
from flask_login import LoginManager

from config import Config
from db import db
from models import User

# -------------------------------
# Create Flask App
# -------------------------------
app = Flask(__name__)
app.config.from_object(Config)

# -------------------------------
# Initialize Extensions
# -------------------------------
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


# -------------------------------
# User Loader for LoginManager
# -------------------------------
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# -------------------------------
# Register Blueprints
# -------------------------------
from routes.auth import auth
from routes.main import main
from routes.messages import messages
from routes.ai import ai

app.register_blueprint(auth)
app.register_blueprint(main)
app.register_blueprint(messages)
app.register_blueprint(ai)


# -------------------------------
# Create Database Tables
# -------------------------------
with app.app_context():
    db.create_all()


# -------------------------------
# Run Flask Server
# -------------------------------
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )