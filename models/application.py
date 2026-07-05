from . import db


class JobApplication(db.Model):

    __tablename__ = "job_applications"

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

    company_name = db.Column(
        db.String(150),
        nullable=False
    )

    role = db.Column(
        db.String(150),
        nullable=False
    )

    location = db.Column(
        db.String(150)
    )

    job_url = db.Column(
        db.String(500)
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="Applied"
    )

    application_date = db.Column(
        db.Date
    )

    interview_date = db.Column(
        db.DateTime
    )

    ctc = db.Column(
        db.String(50)
    )

    notes = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False
    )

    __table_args__ = (
        db.Index(
            "ix_job_application_user_status",
            "user_id",
            "status"
        ),
    )

    def __repr__(self):
        return (
            f"<JobApplication "
            f"{self.company_name} - {self.role}>"
        )