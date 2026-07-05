from models import db

class Resume(db.Model):

    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    phone = db.Column(db.String(20))

    address = db.Column(db.String(250))

    linkedin = db.Column(db.String(250))

    github = db.Column(db.String(250))

    objective = db.Column(db.Text)

    education = db.Column(db.Text)

    experience = db.Column(db.Text)

    projects = db.Column(db.Text)

    certifications = db.Column(db.Text)

    achievements = db.Column(db.Text)

    skills = db.Column(db.Text)