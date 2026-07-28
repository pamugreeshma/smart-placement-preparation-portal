
from datetime import date

from models.task import Task
from models.user_stats import UserStats

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
    # ==========================================
    # TASK + XP + STREAK DASHBOARD DATA
    # ==========================================

    user_stats = UserStats.query.filter_by(
        user_id=current_user.id
    ).first()

    if not user_stats:
        user_stats = UserStats(
            user_id=current_user.id
        )

        db.session.add(user_stats)
        db.session.commit()

    today = date.today()

    today_tasks = (
        Task.query
        .filter(
            Task.user_id == current_user.id,
            Task.due_date == today
        )
        .order_by(
            Task.completed.asc(),
            Task.created_at.desc()
        )
        .limit(5)
        .all()
    )

    pending_tasks_count = (
        Task.query
        .filter_by(
            user_id=current_user.id,
            completed=False
        )
        .count()
    )

    today_completed = (
        Task.query
        .filter(
            Task.user_id == current_user.id,
            Task.completed.is_(True),
            db.func.date(Task.completed_at) == today.isoformat()
        )
        .count()
    )
 # ikkada check cheyyali
    return render_template(
        "dashboard/dashboard.html",
        stats=stats,
        applications=user_applications,
        tasks=today_tasks,
        pending_tasks_count=pending_tasks_count,
        today_completed=today_completed,
        user_stats=user_stats,
        today_tasks=today_tasks,
    )
#till up

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