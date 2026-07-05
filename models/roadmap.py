from . import db


class Roadmap(db.Model):

    __tablename__ = "roadmaps"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    slug = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    icon = db.Column(
        db.String(50),
        default="bi-map"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    topics = db.relationship(
        "RoadmapTopic",
        backref="roadmap",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="RoadmapTopic.position"
    )


class RoadmapTopic(db.Model):

    __tablename__ = "roadmap_topics"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    roadmap_id = db.Column(
        db.Integer,
        db.ForeignKey("roadmaps.id"),
        nullable=False
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    stage = db.Column(
        db.String(100),
        nullable=False
    )

    position = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    estimated_hours = db.Column(
        db.Integer,
        default=1
    )


class UserTopicProgress(db.Model):

    __tablename__ = "user_topic_progress"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    topic_id = db.Column(
        db.Integer,
        db.ForeignKey("roadmap_topics.id"),
        nullable=False
    )

    completed = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    topic = db.relationship(
        "RoadmapTopic",
        backref="progress_records"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "topic_id",
            name="uq_user_topic_progress"
        ),
    )