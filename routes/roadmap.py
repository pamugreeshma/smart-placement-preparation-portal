from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from models import db

from models.roadmap import (
    Roadmap,
    RoadmapTopic,
    UserTopicProgress
)


roadmap = Blueprint(
    "roadmap",
    __name__,
    url_prefix="/roadmaps"
)


@roadmap.route("/")
@login_required
def index():

    roadmaps = Roadmap.query.order_by(
        Roadmap.title.asc()
    ).all()

    roadmap_data = []

    for item in roadmaps:

        total_topics = RoadmapTopic.query.filter_by(
            roadmap_id=item.id
        ).count()

        completed_topics = (
            db.session.query(UserTopicProgress)
            .join(
                RoadmapTopic,
                UserTopicProgress.topic_id == RoadmapTopic.id
            )
            .filter(
                UserTopicProgress.user_id == current_user.id,
                UserTopicProgress.completed.is_(True),
                RoadmapTopic.roadmap_id == item.id
            )
            .count()
        )

        progress = 0

        if total_topics > 0:
            progress = round(
                (completed_topics / total_topics) * 100
            )

        roadmap_data.append({
            "roadmap": item,
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "progress": progress
        })

    return render_template(
        "roadmaps/index.html",
        roadmap_data=roadmap_data
    )


@roadmap.route("/<slug>")
@login_required
def detail(slug):

    selected_roadmap = Roadmap.query.filter_by(
        slug=slug
    ).first_or_404()

    topics = RoadmapTopic.query.filter_by(
        roadmap_id=selected_roadmap.id
    ).order_by(
        RoadmapTopic.position.asc()
    ).all()

    progress_records = UserTopicProgress.query.filter_by(
        user_id=current_user.id
    ).all()

    completed_topic_ids = {
        record.topic_id
        for record in progress_records
        if record.completed
    }

    total_topics = len(topics)

    completed_count = sum(
        1
        for topic in topics
        if topic.id in completed_topic_ids
    )

    progress = 0

    if total_topics > 0:
        progress = round(
            (completed_count / total_topics) * 100
        )

    stages = {}

    for topic in topics:

        if topic.stage not in stages:
            stages[topic.stage] = []

        stages[topic.stage].append(topic)

    return render_template(
        "roadmaps/detail.html",
        roadmap=selected_roadmap,
        stages=stages,
        completed_topic_ids=completed_topic_ids,
        completed_count=completed_count,
        total_topics=total_topics,
        progress=progress
    )


@roadmap.route(
    "/topic/<int:topic_id>/toggle",
    methods=["POST"]
)
@login_required
def toggle_topic(topic_id):

    topic = RoadmapTopic.query.get_or_404(
        topic_id
    )

    progress = UserTopicProgress.query.filter_by(
        user_id=current_user.id,
        topic_id=topic.id
    ).first()

    if not progress:

        progress = UserTopicProgress(
            user_id=current_user.id,
            topic_id=topic.id,
            completed=True,
            completed_at=db.func.now()
        )

        db.session.add(progress)

    else:

        progress.completed = not progress.completed

        if progress.completed:
            progress.completed_at = db.func.now()
        else:
            progress.completed_at = None

    db.session.commit()

    return redirect(
        url_for(
            "roadmap.detail",
            slug=topic.roadmap.slug
        )
    )