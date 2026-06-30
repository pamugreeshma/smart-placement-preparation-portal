from flask import Blueprint, render_template
from flask_login import login_required

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("main/home.html")

@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard/dashboard.html")