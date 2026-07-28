from datetime import datetime

from . import db


class Task(db.Model):

    __tablename__ = "tasks"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    category = db.Column(
        db.String(50),
        nullable=False,
        default="General"
    )

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="Medium"
    )

    due_date = db.Column(
        db.Date,
        nullable=True
    )

    completed = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    xp_reward = db.Column(
        db.Integer,
        nullable=False,
        default=10
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    def __repr__(self):
        return f"<Task {self.title}>"