from datetime import datetime

from . import db


class UserStats(db.Model):

    __tablename__ = "user_stats"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    total_xp = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    current_streak = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    longest_streak = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    last_active_date = db.Column(
        db.Date,
        nullable=True
    )

    tasks_completed = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )