from app import app

from models import db

from models.roadmap import (
    Roadmap,
    RoadmapTopic
)


ROADMAPS = [

    {
        "title": "Software Development Engineer",
        "slug": "software-development-engineer",
        "description": (
            "Master programming, DSA, databases, "
            "backend development and interview preparation."
        ),
        "icon": "bi-code-slash",

        "topics": [

            (
                "Programming Foundations",
                "Programming Fundamentals",
                "Build strong logic using variables, loops, functions and problem solving.",
                1,
                8
            ),

            (
                "Programming Foundations",
                "Object-Oriented Programming",
                "Learn classes, objects, inheritance, polymorphism and abstraction.",
                2,
                8
            ),

            (
                "Data Structures & Algorithms",
                "Arrays and Strings",
                "Master traversal, prefix sums, sliding window and two pointers.",
                3,
                12
            ),

            (
                "Data Structures & Algorithms",
                "Linked Lists",
                "Understand singly, doubly and fast-slow pointer techniques.",
                4,
                8
            ),

            (
                "Data Structures & Algorithms",
                "Stacks and Queues",
                "Solve monotonic stack, queue and deque problems.",
                5,
                8
            ),

            (
                "Data Structures & Algorithms",
                "Trees and Binary Search Trees",
                "Learn traversals, recursion and common tree interview patterns.",
                6,
                14
            ),

            (
                "Data Structures & Algorithms",
                "Graphs",
                "Master BFS, DFS, shortest paths and graph traversal.",
                7,
                16
            ),

            (
                "Core Computer Science",
                "Database Management Systems",
                "Study SQL, normalization, indexing and transactions.",
                8,
                12
            ),

            (
                "Core Computer Science",
                "Operating Systems",
                "Learn processes, threads, scheduling, memory and deadlocks.",
                9,
                12
            ),

            (
                "Core Computer Science",
                "Computer Networks",
                "Understand TCP/IP, HTTP, DNS and networking fundamentals.",
                10,
                10
            ),

            (
                "Development",
                "Backend Development",
                "Build REST APIs, authentication and database-backed applications.",
                11,
                20
            ),

            (
                "Placement Preparation",
                "Resume and Interview Preparation",
                "Prepare projects, behavioral answers and technical interviews.",
                12,
                10
            ),
        ]
    },


    {
        "title": "Data Science & AI",
        "slug": "data-science-ai",
        "description": (
            "Learn Python, statistics, machine learning, "
            "deep learning and portfolio development."
        ),
        "icon": "bi-cpu",

        "topics": [

            (
                "Foundations",
                "Python for Data Science",
                "Master Python syntax, NumPy and data manipulation foundations.",
                1,
                12
            ),

            (
                "Foundations",
                "Statistics and Probability",
                "Learn distributions, estimation and statistical reasoning.",
                2,
                16
            ),

            (
                "Data Analysis",
                "Pandas and Data Cleaning",
                "Clean, transform and explore real datasets.",
                3,
                12
            ),

            (
                "Data Analysis",
                "Data Visualization",
                "Communicate patterns and insights through effective charts.",
                4,
                8
            ),

            (
                "Machine Learning",
                "Supervised Learning",
                "Learn regression, classification and model evaluation.",
                5,
                18
            ),

            (
                "Machine Learning",
                "Unsupervised Learning",
                "Study clustering and dimensionality reduction.",
                6,
                12
            ),

            (
                "Machine Learning",
                "Feature Engineering",
                "Create useful features and robust ML pipelines.",
                7,
                10
            ),

            (
                "Deep Learning",
                "Neural Networks",
                "Understand forward propagation, backpropagation and optimization.",
                8,
                18
            ),

            (
                "Deep Learning",
                "NLP and Transformers",
                "Explore text processing, embeddings and transformer models.",
                9,
                20
            ),

            (
                "Career Projects",
                "End-to-End AI Project",
                "Build, evaluate and present a portfolio-ready AI system.",
                10,
                24
            ),
        ]
    },


    {
        "title": "GATE CSE",
        "slug": "gate-cse",
        "description": (
            "A structured preparation path covering "
            "core CSE subjects, aptitude and revision."
        ),
        "icon": "bi-mortarboard",

        "topics": [

            (
                "Mathematical Foundations",
                "Engineering Mathematics",
                "Cover discrete mathematics, linear algebra, calculus and probability.",
                1,
                30
            ),

            (
                "Programming & DSA",
                "Programming in C",
                "Master pointers, recursion, functions and memory concepts.",
                2,
                18
            ),

            (
                "Programming & DSA",
                "Data Structures",
                "Study arrays, lists, stacks, queues, trees and graphs.",
                3,
                28
            ),

            (
                "Programming & DSA",
                "Algorithms",
                "Master complexity, sorting, searching, greedy and dynamic programming.",
                4,
                30
            ),

            (
                "Systems",
                "Operating Systems",
                "Prepare processes, scheduling, synchronization and memory management.",
                5,
                28
            ),

            (
                "Systems",
                "Computer Networks",
                "Cover network layers, routing, TCP/IP and application protocols.",
                6,
                28
            ),

            (
                "Data & Theory",
                "DBMS",
                "Prepare SQL, normalization, transactions and indexing.",
                7,
                24
            ),

            (
                "Data & Theory",
                "Theory of Computation",
                "Study automata, grammars, decidability and computability.",
                8,
                24
            ),

            (
                "Computer Systems",
                "Computer Organization",
                "Learn CPU, memory hierarchy, pipelines and I/O.",
                9,
                26
            ),

            (
                "Computer Systems",
                "Digital Logic",
                "Cover Boolean algebra, circuits and sequential logic.",
                10,
                20
            ),

            (
                "Final Preparation",
                "Previous Year Questions",
                "Solve and analyze GATE previous-year questions.",
                11,
                50
            ),

            (
                "Final Preparation",
                "Mock Tests and Revision",
                "Use timed mocks, error logs and systematic revision.",
                12,
                45
            ),
        ]
    }
]


def seed():

    for roadmap_data in ROADMAPS:

        existing = Roadmap.query.filter_by(
            slug=roadmap_data["slug"]
        ).first()

        if existing:
            print(
                f"Skipping existing roadmap: "
                f"{roadmap_data['title']}"
            )
            continue

        new_roadmap = Roadmap(
            title=roadmap_data["title"],
            slug=roadmap_data["slug"],
            description=roadmap_data["description"],
            icon=roadmap_data["icon"]
        )

        db.session.add(new_roadmap)

        db.session.flush()

        for (
            stage,
            title,
            description,
            position,
            estimated_hours
        ) in roadmap_data["topics"]:

            topic = RoadmapTopic(
                roadmap_id=new_roadmap.id,
                stage=stage,
                title=title,
                description=description,
                position=position,
                estimated_hours=estimated_hours
            )

            db.session.add(topic)

    db.session.commit()

    print("CareerForge roadmaps seeded successfully.")


if __name__ == "__main__":

    with app.app_context():
        db.create_all()
        seed()