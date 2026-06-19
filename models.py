from db import db
from flask_login import UserMixin
from datetime import datetime


# ==========================
# USER MODEL
# ==========================
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Location
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    posts = db.relationship("Post", backref="author", lazy=True)

    sent_messages = db.relationship(
        "Message",
        foreign_keys="Message.sender_id",
        backref="sender",
        lazy=True
    )

    received_messages = db.relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        backref="receiver",
        lazy=True
    )

    def __repr__(self):
        return f"<User {self.username}>"



# ==========================
# POST MODEL
# ==========================
class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=True)

    # Location per post (optional but useful for nearby search)
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Post {self.id} by User {self.user_id}>"



# ==========================
# MESSAGE MODEL
# ==========================
class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message {self.id} from {self.sender_id} to {self.receiver_id}>"


class AgentMemory(db.Model):
    __tablename__ = "agent_memory"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    role = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AgentMemory {self.id} user={self.user_id} role={self.role}>"



class KnowledgeChunk(db.Model):
    __tablename__ = "knowledge_chunks"

    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String(50), nullable=False, index=True)
    source_id = db.Column(db.Integer, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    text = db.Column(db.Text, nullable=False)
    embedding_json = db.Column(db.Text, nullable=False)
    meta_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<KnowledgeChunk {self.id} {self.source_type}:{self.source_id}>"


class AIAutomationTask(db.Model):
    __tablename__ = "ai_automation_tasks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    task_type = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)
    last_run_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AIAutomationTask {self.id} {self.task_type} user={self.user_id}>"
