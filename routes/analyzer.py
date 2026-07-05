import os
from uuid import uuid4

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)

from flask_login import (
    login_required,
    current_user
)

from werkzeug.utils import secure_filename
from pypdf import PdfReader

from models import db
from models.resume_analysis import ResumeAnalysis
from utils.resume_analyzer import analyze_resume


analyzer = Blueprint(
    "analyzer",
    __name__,
    url_prefix="/analyzer"
)


ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def extract_pdf_text(file_path):

    reader = PdfReader(file_path)

    text_parts = []

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text_parts.append(page_text)

    return "\n".join(text_parts)


@analyzer.route("/", methods=["GET", "POST"])
@login_required
def upload_resume():

    if request.method == "POST":

        if "resume" not in request.files:

            flash(
                "Please select a resume PDF.",
                "warning"
            )

            return redirect(
                url_for("analyzer.upload_resume")
            )

        file = request.files["resume"]

        if not file or file.filename == "":

            flash(
                "Please select a resume PDF.",
                "warning"
            )

            return redirect(
                url_for("analyzer.upload_resume")
            )

        if not allowed_file(file.filename):

            flash(
                "Only PDF resumes are supported.",
                "danger"
            )

            return redirect(
                url_for("analyzer.upload_resume")
            )

        original_filename = secure_filename(
            file.filename
        )

        unique_filename = (
            f"{current_user.id}_"
            f"{uuid4().hex}_"
            f"{original_filename}"
        )

        upload_folder = os.path.join(
            current_app.root_path,
            "static",
            "uploads",
            "resumes"
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        file_path = os.path.join(
            upload_folder,
            unique_filename
        )

        file.save(file_path)

        try:

            extracted_text = extract_pdf_text(
                file_path
            )

            if not extracted_text.strip():

                flash(
                    "No readable text was found. The PDF may be scanned or image-based.",
                    "danger"
                )

                return redirect(
                    url_for("analyzer.upload_resume")
                )

            result = analyze_resume(
                extracted_text
            )

            analysis = ResumeAnalysis(

                user_id=current_user.id,

                file_name=original_filename,

                ats_score=result["ats_score"],

                detected_skills="|".join(
                    result["detected_skills"]
                ),

                missing_skills="|".join(
                    result["missing_skills"]
                ),

                suggestions="|".join(
                    result["suggestions"]
                )
            )

            db.session.add(analysis)
            db.session.commit()

            return render_template(
                "analyzer/result.html",
                result=result,
                analysis=analysis
            )

        except Exception as error:

            db.session.rollback()

            current_app.logger.exception(
                "Resume analysis failed"
            )

            flash(
                f"Resume analysis failed: {error}",
                "danger"
            )

            return redirect(
                url_for("analyzer.upload_resume")
            )

    analyses = (
        ResumeAnalysis.query
        .filter_by(user_id=current_user.id)
        .order_by(ResumeAnalysis.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "analyzer/upload.html",
        analyses=analyses
    )