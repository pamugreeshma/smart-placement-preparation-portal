from datetime import datetime, date, timedelta

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from models import db
from models.task import Task
from models.user_stats import UserStats


tasks = Blueprint(
    "tasks",
    __name__,
    url_prefix="/tasks"
)


CATEGORIES = [
    "DSA",
    "Aptitude",
    "Core CS",
    "Development",
    "Interview",
    "GATE",
    "General"
]


PRIORITIES = [
    "Low",
    "Medium",
    "High"
]


def get_user_stats():

    stats = UserStats.query.filter_by(
        user_id=current_user.id
    ).first()

    if not stats:

        stats = UserStats(
            user_id=current_user.id
        )

        db.session.add(stats)
        db.session.commit()

    return stats


def calculate_xp(priority):

    rewards = {
        "Low": 10,
        "Medium": 20,
        "High": 30
    }

    return rewards.get(priority, 10)


def update_streak(stats):

    today = date.today()

    if stats.last_active_date is None:

        stats.current_streak = 1

    elif stats.last_active_date == today:

        return

    elif stats.last_active_date == today - timedelta(days=1):

        stats.current_streak += 1

    else:

        stats.current_streak = 1

    stats.last_active_date = today

    if stats.current_streak > stats.longest_streak:

        stats.longest_streak = stats.current_streak


@tasks.route("/")
@login_required
def index():

    user_tasks = (
        Task.query
        .filter_by(user_id=current_user.id)
        .order_by(
            Task.completed.asc(),
            Task.due_date.asc(),
            Task.created_at.desc()
        )
        .all()
    )

    stats = get_user_stats()

    total_tasks = len(user_tasks)

    completed_tasks = sum(
        1 for task in user_tasks
        if task.completed
    )

    pending_tasks = total_tasks - completed_tasks

    completion_rate = 0

    if total_tasks:
        completion_rate = round(
            completed_tasks / total_tasks * 100
        )

    return render_template(
        "tasks/index.html",
        tasks=user_tasks,
        stats=stats,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        completion_rate=completion_rate
    )


@tasks.route(
    "/add",
    methods=["GET", "POST"]
)
@login_required
def add():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        category = request.form.get(
            "category",
            "General"
        )

        priority = request.form.get(
            "priority",
            "Medium"
        )

        due_date_raw = request.form.get(
            "due_date",
            ""
        )

        if not title:

            flash(
                "Task title is required.",
                "danger"
            )

            return render_template(
                "tasks/form.html",
                categories=CATEGORIES,
                priorities=PRIORITIES
            )

        if category not in CATEGORIES:
            category = "General"

        if priority not in PRIORITIES:
            priority = "Medium"

        due_date = None

        if due_date_raw:

            try:

                due_date = datetime.strptime(
                    due_date_raw,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                flash(
                    "Invalid due date.",
                    "danger"
                )

                return render_template(
                    "tasks/form.html",
                    categories=CATEGORIES,
                    priorities=PRIORITIES
                )

        task = Task(
            user_id=current_user.id,
            title=title,
            description=description or None,
            category=category,
            priority=priority,
            due_date=due_date,
            xp_reward=calculate_xp(priority)
        )

        db.session.add(task)
        db.session.commit()

        flash(
            "Task added successfully.",
            "success"
        )

        return redirect(
            url_for("tasks.index")
        )

    return render_template(
        "tasks/form.html",
        categories=CATEGORIES,
        priorities=PRIORITIES
    )


@tasks.route(
    "/<int:task_id>/complete",
    methods=["POST"]
)
@login_required
def complete(task_id):

    task = (
        Task.query
        .filter_by(
            id=task_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    # Prevent duplicate XP
    if task.completed:

        flash(
            "Task is already completed.",
            "info"
        )

        return redirect(
            url_for("tasks.index")
        )

    task.completed = True
    task.completed_at = datetime.utcnow()

    stats = get_user_stats()

    stats.total_xp += task.xp_reward
    stats.tasks_completed += 1

    update_streak(stats)

    db.session.commit()

    flash(
        f"Task completed! +{task.xp_reward} XP",
        "success"
    )

    return redirect(
        url_for("tasks.index")
    )


@tasks.route(
    "/<int:task_id>/delete",
    methods=["POST"]
)
@login_required
def delete(task_id):

    task = (
        Task.query
        .filter_by(
            id=task_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    db.session.delete(task)
    db.session.commit()

    flash(
        "Task deleted.",
        "success"
    )

    return redirect(
        url_for("tasks.index")
    )