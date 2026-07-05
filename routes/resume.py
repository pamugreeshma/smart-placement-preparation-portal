from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask import send_file
from io import BytesIO

from utils.resume_generator import generate_resume_pdf
from models import db
from models.resume import Resume

resume = Blueprint(
    "resume",
    __name__,
    url_prefix="/resume"
)


@resume.route("/", methods=["GET", "POST"])
@login_required
def builder():

    user_resume = Resume.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":

        if not user_resume:
            user_resume = Resume(user_id=current_user.id)

        user_resume.phone = request.form.get("phone")
        user_resume.address = request.form.get("address")
        user_resume.linkedin = request.form.get("linkedin")
        user_resume.github = request.form.get("github")
        user_resume.objective = request.form.get("objective")
        user_resume.education = request.form.get("education")
        user_resume.experience = request.form.get("experience")
        user_resume.projects = request.form.get("projects")
        user_resume.certifications = request.form.get("certifications")
        user_resume.achievements = request.form.get("achievements")
        user_resume.skills = request.form.get("skills")

        db.session.add(user_resume)
        db.session.commit()

        flash("Resume saved successfully!", "success")

        return redirect(url_for("resume.builder"))

    return render_template(
        "resume/resume_form.html",
        resume=user_resume
    )
@resume.route("/preview")
@login_required
def preview():

    user_resume = Resume.query.filter_by(
        user_id=current_user.id
    ).first()

    return render_template(
        "resume/preview.html",
        resume=user_resume
    )
@resume.route("/download")
@login_required
def download():

    user_resume = Resume.query.filter_by(
        user_id=current_user.id
    ).first()

    pdf = generate_resume_pdf(
        current_user,
        user_resume
    )

    return send_file(

        BytesIO(pdf),

        download_name="CareerForge_Resume.pdf",

        as_attachment=True,

        mimetype="application/pdf"

    )
