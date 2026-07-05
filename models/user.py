from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    # ----------------------------
    # Profile Information
    # ----------------------------

    college = db.Column(db.String(150))

    branch = db.Column(db.String(100))

    graduation_year = db.Column(db.Integer)

    skills = db.Column(db.Text)

    dream_company = db.Column(db.String(150))

    bio = db.Column(db.Text)

    profile_image = db.Column(
        db.String(255),
        default="default.png"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # ----------------------------

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )