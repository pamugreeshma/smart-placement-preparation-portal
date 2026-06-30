from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

from models import db
from models.user import User

auth = Blueprint("auth", __name__, url_prefix="/auth")


# -------------------------
# Register
# -------------------------

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:

            flash("Email already exists.", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(
            full_name=full_name,
            email=email
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful! Please Login.", "success")

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# -------------------------
# Login
# -------------------------

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            login_user(user)

            return redirect(url_for("main.dashboard"))

        flash("Invalid Email or Password", "danger")

    return render_template("auth/login.html")


# -------------------------
# Logout
# -------------------------

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "success")

    return redirect(url_for("main.home"))