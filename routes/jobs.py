import os
import sys
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

jobs = Blueprint("jobs", __name__, url_prefix="/jobs")


def get_curated_data():
    """
    Load and normalize curated sector and job data from the teammate project.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    possible_paths = [
        os.path.join(base_dir, "..", "Downloads", "career zip", "project 1"),
        os.path.join(base_dir, "..", "career zip", "project 1"),
        r"C:\Users\pamug\Downloads\career zip\project 1",
    ]

    sectors_data = {}
    for p in possible_paths:
        abs_p = os.path.abspath(p)
        if os.path.exists(abs_p):
            if abs_p not in sys.path:
                sys.path.insert(0, abs_p)
            try:
                from career_data.sectors import SECTORS
                sectors_data = SECTORS
                break
            except Exception:
                pass

    sectors_list = []
    all_jobs = []

    for sec_id, sec_data in sectors_data.items():
        sec_title = sec_data.get("title", sec_id.replace("_", " ").title())
        sec_emoji = sec_data.get("emoji", "💼")

        job_items = []
        if "jobs" in sec_data:
            job_items = sec_data["jobs"]
        elif "departments" in sec_data:
            for dep_id, dep_data in sec_data["departments"].items():
                dep_title = dep_data.get("title", dep_id.replace("_", " ").title())
                for j in dep_data.get("jobs", []):
                    j_copy = dict(j)
                    j_copy["department"] = dep_title
                    job_items.append(j_copy)

        sec_jobs_normalized = []
        for j_item in job_items:
            norm_job = {
                "slug": j_item.get("slug", ""),
                "title": j_item.get("title", ""),
                "sector_id": sec_id,
                "sector_title": sec_title,
                "sector_emoji": sec_emoji,
                "department": j_item.get("department", ""),
                "description": j_item.get("full_description", ""),
                "degree": j_item.get("degree", ""),
                "age": j_item.get("age", ""),
                "skills": j_item.get("skills", ""),
                "experience": j_item.get("experience", ""),
                "pay": j_item.get("pay", {}),
                "apply_link": j_item.get("apply_link", ""),
                "selection_process": j_item.get("selection_process", ""),
                "career_growth": j_item.get("career_growth", ""),
                "roadmap": j_item.get("roadmap", ""),
                "resume_tips": j_item.get("resume_tips", ""),
                "notes": j_item.get("notes", ""),
                "recruitment_status": j_item.get("recruitment_status", ""),
                "minimum_score": j_item.get("minimum_score", ""),
                "apply_dates": j_item.get("apply_dates", ""),
                "apply_deadline": j_item.get("apply_deadline", ""),
                "exam_dates": j_item.get("exam_dates", ""),
            }
            sec_jobs_normalized.append(norm_job)
            all_jobs.append(norm_job)

        sectors_list.append({
            "id": sec_id,
            "title": sec_title,
            "emoji": sec_emoji,
            "count": len(sec_jobs_normalized)
        })

    return sectors_list, all_jobs


@jobs.route("/", methods=["GET"])
@login_required
def index():
    """
    Job module landing page with browsing, search, and details.
    """
    sectors_list, all_jobs = get_curated_data()

    search_query = request.args.get("q", "").strip()
    active_sector = request.args.get("sector", "all").strip()
    selected_job_slug = request.args.get("job", "").strip()

    filtered_jobs = all_jobs

    if active_sector and active_sector != "all":
        filtered_jobs = [j for j in filtered_jobs if j["sector_id"] == active_sector]

    if search_query:
        q_lower = search_query.lower()
        filtered_jobs = [
            j for j in filtered_jobs
            if q_lower in j["title"].lower()
            or q_lower in j["description"].lower()
            or q_lower in j["skills"].lower()
            or q_lower in j["sector_title"].lower()
            or q_lower in j["department"].lower()
        ]

    selected_job = None
    if selected_job_slug:
        for j in all_jobs:
            if j["slug"] == selected_job_slug:
                selected_job = j
                break

    username = current_user.full_name if (current_user and hasattr(current_user, "full_name") and current_user.full_name) else "User"

    return render_template(
        "jobs/index.html",
        sectors=sectors_list,
        jobs=filtered_jobs,
        total_jobs_count=len(all_jobs),
        filtered_count=len(filtered_jobs),
        active_sector=active_sector,
        search_query=search_query,
        selected_job=selected_job,
        username=username
    )
