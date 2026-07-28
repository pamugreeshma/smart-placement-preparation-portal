from routes.analyzer import analyzer

from routes.applications import applications

from models.application import JobApplication

from routes.main import main

from routes.auth import auth

from models.task import Task

from models.user_stats import UserStats

from flask import Flask, render_template

from flask_login import LoginManager

from config import Config

from routes.tasks import tasks

from models import db

from models.user import User

from models.resume import Resume
from models.roadmap import (
    Roadmap,
    RoadmapTopic,
    UserTopicProgress
)

from routes.resume import resume

from routes.roadmap import roadmap

from routes.interview import interview


login_manager = LoginManager()


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    with app.app_context():
        db.create_all()

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(resume)
    app.register_blueprint(analyzer)
    app.register_blueprint(roadmap)
    app.register_blueprint(applications)
    app.register_blueprint(tasks)
    app.register_blueprint(interview)
    return app


@login_manager.user_loader
def load_user(user_id):

    return db.session.get(User, int(user_id))


app = create_app()


if __name__ == "__main__":

    app.run(debug=True)