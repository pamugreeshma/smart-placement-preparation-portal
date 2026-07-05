from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db

from models.roadmap import (
    Roadmap,
    RoadmapTopic,
    UserTopicProgress
)
from models.resume_analysis import ResumeAnalysis

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("main/home.html")

@main.route("/dashboard")
@login_required
def dashboard():

    from models.application import JobApplication
    from models.resume import Resume

    # -----------------------------------------
    # REAL JOB APPLICATION STATISTICS
    # -----------------------------------------

    user_applications = (
        JobApplication.query
        .filter_by(user_id=current_user.id)
        .all()
    )

    total_applications = len(user_applications)

    interview_count = sum(
        1 for application in user_applications
        if application.status == "Interview"
    )

    offer_count = sum(
        1 for application in user_applications
        if application.status == "Offer"
    )

    # -----------------------------------------
    # REAL RESUME STATUS
    # -----------------------------------------

    user_resume = (
        Resume.query
        .filter_by(user_id=current_user.id)
        .first()
    )

    resume_completed = user_resume is not None

    # -----------------------------------------
    # DASHBOARD STATS
    # -----------------------------------------

    stats = {
        "applications": total_applications,
        "interviews": interview_count,
        "offers": offer_count,
        "resume_completed": resume_completed
    }

    return render_template(
        "dashboard/dashboard.html",
        stats=stats,
        applications=user_applications
    )

@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if request.method == "POST":

        current_user.full_name = request.form.get("full_name")
        current_user.college = request.form.get("college")
        current_user.branch = request.form.get("branch")

        graduation_year = request.form.get("graduation_year")

        if graduation_year:
            current_user.graduation_year = int(graduation_year)

        current_user.skills = request.form.get("skills")
        current_user.dream_company = request.form.get("dream_company")
        current_user.bio = request.form.get("bio")

        db.session.commit()

        flash("Profile updated successfully!", "success")

        return redirect(url_for("main.profile"))

    return render_template("profile/profile.html")