from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from models import db
from models.application import JobApplication


applications = Blueprint(
    "applications",
    __name__,
    url_prefix="/applications"
)


# =========================================================
# APPLICATION TRACKER DASHBOARD
# =========================================================

@applications.route("/")
@login_required
def index():

    selected_status = request.args.get(
        "status",
        "",
        type=str
    ).strip()

    search_query = request.args.get(
        "q",
        "",
        type=str
    ).strip()

    query = JobApplication.query.filter_by(
        user_id=current_user.id
    )

    # Filter by status
    if selected_status:
        query = query.filter(
            JobApplication.status == selected_status
        )

    # Search by company or role
    if search_query:
        search_pattern = f"%{search_query}%"

        query = query.filter(
            db.or_(
                JobApplication.company_name.ilike(
                    search_pattern
                ),
                JobApplication.role.ilike(
                    search_pattern
                )
            )
        )

    job_applications = query.order_by(
        JobApplication.created_at.desc()
    ).all()

    # Real statistics from database
    all_user_applications = (
        JobApplication.query
        .filter_by(user_id=current_user.id)
        .all()
    )

    stats = {
        "total": len(all_user_applications),

        "applied": sum(
            1 for item in all_user_applications
            if item.status == "Applied"
        ),

        "interview": sum(
            1 for item in all_user_applications
            if item.status == "Interview"
        ),

        "offer": sum(
            1 for item in all_user_applications
            if item.status == "Offer"
        ),

        "rejected": sum(
            1 for item in all_user_applications
            if item.status == "Rejected"
        )
    }

    return render_template(
        "applications/index.html",
        applications=job_applications,
        stats=stats,
        selected_status=selected_status,
        search_query=search_query
    )


# =========================================================
# ADD APPLICATION
# =========================================================

@applications.route(
    "/add",
    methods=["GET", "POST"]
)
@login_required
def add():

    if request.method == "POST":

        company_name = request.form.get(
            "company_name",
            ""
        ).strip()

        role = request.form.get(
            "role",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        job_url = request.form.get(
            "job_url",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "Applied"
        ).strip()

        application_date_raw = request.form.get(
            "application_date",
            ""
        ).strip()

        ctc = request.form.get(
            "ctc",
            ""
        ).strip()

        notes = request.form.get(
            "notes",
            ""
        ).strip()

        # Validation
        if not company_name or not role:
            flash(
                "Company name and role are required.",
                "danger"
            )

            return render_template(
                "applications/form.html",
                application=None
            )

        valid_statuses = {
            "Wishlist",
            "Applied",
            "Assessment",
            "Interview",
            "Offer",
            "Rejected"
        }

        if status not in valid_statuses:
            status = "Applied"

        application_date = None

        if application_date_raw:
            try:
                application_date = datetime.strptime(
                    application_date_raw,
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                flash(
                    "Invalid application date.",
                    "danger"
                )

                return render_template(
                    "applications/form.html",
                    application=None
                )

        new_application = JobApplication(
            user_id=current_user.id,
            company_name=company_name,
            role=role,
            location=location or None,
            job_url=job_url or None,
            status=status,
            application_date=application_date,
            ctc=ctc or None,
            notes=notes or None
        )

        db.session.add(new_application)
        db.session.commit()

        flash(
            "Application added successfully.",
            "success"
        )

        return redirect(
            url_for("applications.index")
        )

    return render_template(
        "applications/form.html",
        application=None
    )


# =========================================================
# EDIT APPLICATION
# =========================================================

@applications.route(
    "/<int:application_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit(application_id):

    job_application = (
        JobApplication.query
        .filter_by(
            id=application_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    if request.method == "POST":

        company_name = request.form.get(
            "company_name",
            ""
        ).strip()

        role = request.form.get(
            "role",
            ""
        ).strip()

        if not company_name or not role:
            flash(
                "Company name and role are required.",
                "danger"
            )

            return render_template(
                "applications/form.html",
                application=job_application
            )

        status = request.form.get(
            "status",
            "Applied"
        ).strip()

        valid_statuses = {
            "Wishlist",
            "Applied",
            "Assessment",
            "Interview",
            "Offer",
            "Rejected"
        }

        if status not in valid_statuses:
            status = "Applied"

        application_date_raw = request.form.get(
            "application_date",
            ""
        ).strip()

        application_date = None

        if application_date_raw:
            try:
                application_date = datetime.strptime(
                    application_date_raw,
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                flash(
                    "Invalid application date.",
                    "danger"
                )

                return render_template(
                    "applications/form.html",
                    application=job_application
                )

        job_application.company_name = company_name
        job_application.role = role

        job_application.location = (
            request.form.get("location", "").strip()
            or None
        )

        job_application.job_url = (
            request.form.get("job_url", "").strip()
            or None
        )

        job_application.status = status

        job_application.application_date = (
            application_date
        )

        job_application.ctc = (
            request.form.get("ctc", "").strip()
            or None
        )

        job_application.notes = (
            request.form.get("notes", "").strip()
            or None
        )

        db.session.commit()

        flash(
            "Application updated successfully.",
            "success"
        )

        return redirect(
            url_for("applications.index")
        )

    return render_template(
        "applications/form.html",
        application=job_application
    )


# =========================================================
# QUICK STATUS UPDATE
# =========================================================

@applications.route(
    "/<int:application_id>/status",
    methods=["POST"]
)
@login_required
def update_status(application_id):

    job_application = (
        JobApplication.query
        .filter_by(
            id=application_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    new_status = request.form.get(
        "status",
        ""
    ).strip()

    valid_statuses = {
        "Wishlist",
        "Applied",
        "Assessment",
        "Interview",
        "Offer",
        "Rejected"
    }

    if new_status not in valid_statuses:
        flash(
            "Invalid application status.",
            "danger"
        )

        return redirect(
            url_for("applications.index")
        )

    job_application.status = new_status

    db.session.commit()

    flash(
        "Application status updated.",
        "success"
    )

    return redirect(
        url_for("applications.index")
    )


# =========================================================
# DELETE APPLICATION
# =========================================================

@applications.route(
    "/<int:application_id>/delete",
    methods=["POST"]
)
@login_required
def delete(application_id):

    job_application = (
        JobApplication.query
        .filter_by(
            id=application_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    db.session.delete(job_application)
    db.session.commit()

    flash(
        "Application deleted successfully.",
        "success"
    )

    return redirect(
        url_for("applications.index")
    )