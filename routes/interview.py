import random
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask_login import login_required, current_user

interview = Blueprint(
    "interview",
    __name__,
    url_prefix="/interview"
)

# ---------------------------------------------------------
# Static Question Pools (adapted from teammate implementation)
# ---------------------------------------------------------
hr_questions = [
    "Tell me about yourself.",
    "What are your strengths?",
    "What are your weaknesses?",
    "Why should we hire you?",
    "Where do you see yourself in 5 years?"
]

technical_questions = [
    "What is Python?",
    "What is OOP?",
    "What is a Function?",
    "Difference between List and Tuple?",
    "What is SQL?"
]

aptitude_questions = [
    {
        "question": "What is 25 + 15 ?",
        "answer": "40"
    },
    {
        "question": "What is 50% of 200 ?",
        "answer": "100"
    },
    {
        "question": "What is 12 × 8 ?",
        "answer": "96"
    }
]

python_questions = [
    "What is Python?",
    "What is OOP?",
    "What is Inheritance?",
    "What is Polymorphism?",
    "What is Encapsulation?",
    "What is Abstraction?",
    "What is a Function?",
    "What is a Lambda Function?",
    "What is a List?",
    "What is a Tuple?",
    "What is a Dictionary?",
    "What is a Set?",
    "What is Exception Handling?",
    "What is a Module?",
    "What is a Package?",
    "What is Flask?",
    "What is Django?",
    "What is an API?",
    "What is JSON?",
    "What is SQL?",
    "What is a Loop?",
    "What is a Class?",
    "What is an Object?",
    "What is Method Overriding?",
    "What is Method Overloading?"
]

testing_questions = [
    "What is Software Testing?",
    "What is SDLC?",
    "What is STLC?",
    "What is a Test Case?",
    "What is a Test Scenario?",
    "What is Regression Testing?",
    "What is Retesting?",
    "What is Smoke Testing?",
    "What is Sanity Testing?",
    "What is Black Box Testing?",
    "What is White Box Testing?",
    "What is Functional Testing?",
    "What is Non-Functional Testing?",
    "What is UAT (User Acceptance Testing)?",
    "What is Bug Life Cycle?",
    "What is Severity and Priority?",
    "What is Selenium?",
    "What is Automation Testing?",
    "What is Manual Testing?",
    "What is Integration Testing?",
    "What is System Testing?",
    "What is Alpha Testing?",
    "What is Beta Testing?",
    "What is Test Plan?",
    "What is Test Strategy?"
]

data_analyst_questions = [
    "What is Data Analysis?",
    "What is SQL?",
    "What is a Primary Key?",
    "What is a Foreign Key?",
    "What is a JOIN in SQL?",
    "What are the types of JOINs?",
    "What is GROUP BY in SQL?",
    "What is a Database?",
    "What is Data Cleaning?",
    "What is Data Visualization?",
    "What is Power BI?",
    "What is Tableau?",
    "What is Microsoft Excel?",
    "What is a Pivot Table?",
    "What is a Dashboard?",
    "What is ETL?",
    "What is Data Warehousing?",
    "What is KPI?",
    "What is Data Mining?",
    "What is a Bar Chart?",
    "What is a Pie Chart?",
    "What is a Scatter Plot?",
    "What is Python used for in Data Analysis?",
    "What is Pandas?",
    "What is NumPy?"
]


# ---------------------------------------------------------
# Blueprint Routes
# ---------------------------------------------------------

@interview.route("/")
@login_required
def index():
    """Main Interview Practice Portal hub."""
    username = current_user.full_name if (current_user and current_user.is_authenticated) else "Student"
    return render_template(
        "interview/index.html",
        username=username
    )


@interview.route("/categories", methods=["POST"])
@login_required
def categories():
    """Handle category selection / username form submission."""
    name = request.form.get("name", getattr(current_user, "full_name", "Student"))
    return render_template(
        "interview/index.html",
        username=name
    )


@interview.route("/hr")
@login_required
def hr():
    """HR Interview Practice Questions."""
    return render_template(
        "interview/question_list.html",
        questions=hr_questions,
        title="HR Interview Questions"
    )


@interview.route("/technical")
@login_required
def technical():
    """Technical Interview Practice Questions."""
    return render_template(
        "interview/question_list.html",
        questions=technical_questions,
        title="Technical Interview Questions"
    )


@interview.route("/python")
@login_required
def python_developer():
    """Python Developer Interview Questions."""
    random_questions = random.sample(
        python_questions,
        min(5, len(python_questions))
    )
    return render_template(
        "interview/question_list.html",
        questions=random_questions,
        title="Python Developer Interview"
    )


@interview.route("/tester")
@login_required
def tester():
    """Software Tester Interview Questions."""
    random_questions = random.sample(
        testing_questions,
        min(5, len(testing_questions))
    )
    return render_template(
        "interview/question_list.html",
        questions=random_questions,
        title="Software Tester Interview"
    )


@interview.route("/analyst")
@login_required
def analyst():
    """Data Analyst Interview Questions."""
    random_questions = random.sample(
        data_analyst_questions,
        min(5, len(data_analyst_questions))
    )
    return render_template(
        "interview/question_list.html",
        questions=random_questions,
        title="Data Analyst Interview"
    )


@interview.route("/aptitude")
@login_required
def aptitude():
    """Aptitude Test Questions."""
    return render_template(
        "interview/aptitude.html",
        questions=aptitude_questions
    )


@interview.route("/aptitude_result", methods=["POST"])
@login_required
def aptitude_result():
    """Evaluate Aptitude Test submission."""
    correct_answers = ["40", "100", "96"]
    results = []
    score = 0

    for i in range(1, 4):
        user_answer = request.form.get(f"answer{i}", "").strip()
        correct_answer = correct_answers[i - 1]
        is_correct = (user_answer == correct_answer)

        if is_correct:
            score += 1

        results.append({
            "question_no": i,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })

    return render_template(
        "interview/aptitude_result.html",
        score=score,
        results=results
    )


@interview.route("/result", methods=["POST"])
@login_required
def result():
    """Evaluate Static Question submission."""
    answers = request.form
    total_answers = 0

    for answer in answers.values():
        if answer.strip() != "":
            total_answers += 1

    if total_answers >= 5:
        feedback = "Outstanding performance! You attempted all questions."
    elif total_answers >= 3:
        feedback = "Good job! Continue practicing to improve confidence."
    else:
        feedback = "You need more interview practice. Try answering all questions."

    return render_template(
        "interview/result.html",
        total_answers=total_answers,
        feedback=feedback
    )


@interview.route("/ai/<role>/<level>")
@login_required
def ai_interview(role, level):
    """Phase 2 AI Interview entry point stub."""
    flash(
        f"AI Interview Practice for {role.capitalize()} ({level.capitalize()}) will be enabled in Phase 2 with Gemini API integration.",
        "info"
    )
    return redirect(url_for("interview.index"))
