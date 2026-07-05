import re


SKILL_KEYWORDS = {
    "Python": ["python"],
    "Java": ["java"],
    "C": [" c ", "c programming"],
    "C++": ["c++"],
    "JavaScript": ["javascript", "js"],
    "HTML": ["html"],
    "CSS": ["css"],
    "SQL": ["sql"],
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MongoDB": ["mongodb"],
    "Flask": ["flask"],
    "Django": ["django"],
    "FastAPI": ["fastapi"],
    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node.js", "nodejs"],
    "Git": ["git"],
    "GitHub": ["github"],
    "Docker": ["docker"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "Linux": ["linux"],
    "REST API": ["rest api", "restful api", "restful"],
    "Machine Learning": ["machine learning"],
    "Deep Learning": ["deep learning"],
    "Data Structures": ["data structures", "dsa"],
    "Algorithms": ["algorithms"],
    "DBMS": ["dbms", "database management system"],
    "Operating Systems": ["operating systems", "operating system"],
    "Computer Networks": ["computer networks", "computer networking"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"]
}


RECOMMENDED_CSE_SKILLS = [
    "Python",
    "Java",
    "SQL",
    "Git",
    "GitHub",
    "Data Structures",
    "Algorithms",
    "DBMS",
    "Operating Systems",
    "Computer Networks",
    "REST API"
]


SECTION_KEYWORDS = {
    "Summary": [
        "summary",
        "professional summary",
        "career objective",
        "objective",
        "profile"
    ],

    "Education": [
        "education",
        "academic background",
        "academics",
        "qualification"
    ],

    "Skills": [
        "skills",
        "technical skills",
        "core competencies",
        "technologies"
    ],

    "Experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment"
    ],

    "Projects": [
        "projects",
        "academic projects",
        "personal projects"
    ],

    "Certifications": [
        "certifications",
        "certificates",
        "courses"
    ],

    "Achievements": [
        "achievements",
        "awards",
        "honors"
    ]
}


ACTION_VERBS = [
    "developed",
    "built",
    "designed",
    "implemented",
    "created",
    "improved",
    "optimized",
    "managed",
    "led",
    "automated",
    "deployed",
    "integrated",
    "reduced",
    "increased",
    "analyzed",
    "engineered"
]


def normalize_text(text):
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_email(text):
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    return bool(re.search(pattern, text))


def detect_phone(text):
    pattern = r"(\+?\d[\d\s\-()]{8,}\d)"
    return bool(re.search(pattern, text))


def detect_linkedin(text):
    return "linkedin.com" in text.lower()


def detect_github(text):
    return "github.com" in text.lower()


def detect_sections(text):
    lower_text = text.lower()

    detected = []
    missing = []

    for section, keywords in SECTION_KEYWORDS.items():

        if any(keyword in lower_text for keyword in keywords):
            detected.append(section)

        else:
            missing.append(section)

    return detected, missing


def detect_skills(text):
    lower_text = f" {text.lower()} "

    detected = []

    for skill, keywords in SKILL_KEYWORDS.items():

        if any(keyword in lower_text for keyword in keywords):
            detected.append(skill)

    return sorted(set(detected))


def detect_missing_skills(detected_skills):
    return [
        skill
        for skill in RECOMMENDED_CSE_SKILLS
        if skill not in detected_skills
    ]


def count_action_verbs(text):
    lower_text = text.lower()

    return sum(
        len(re.findall(rf"\b{re.escape(verb)}\b", lower_text))
        for verb in ACTION_VERBS
    )


def count_metrics(text):
    patterns = [
        r"\b\d+%",
        r"\b\d+\+",
        r"\b\d{2,}\b",
        r"\b\d+x\b"
    ]

    return sum(
        len(re.findall(pattern, text, flags=re.IGNORECASE))
        for pattern in patterns
    )


def calculate_ats_score(
    text,
    detected_skills,
    detected_sections
):

    score = 0

    # Contact information: 15
    if detect_email(text):
        score += 6

    if detect_phone(text):
        score += 5

    if detect_linkedin(text) or detect_github(text):
        score += 4

    # Resume sections: 25
    important_sections = [
        "Education",
        "Skills",
        "Experience",
        "Projects",
        "Summary"
    ]

    for section in important_sections:
        if section in detected_sections:
            score += 5

    # Technical skills: 25
    skill_score = min(
        len(detected_skills) * 3,
        25
    )

    score += skill_score

    # Action verbs: 15
    action_count = count_action_verbs(text)

    score += min(
        action_count * 3,
        15
    )

    # Measurable achievements: 10
    metric_count = count_metrics(text)

    score += min(
        metric_count * 2,
        10
    )

    # Resume text depth: 10
    word_count = len(text.split())

    if 250 <= word_count <= 900:
        score += 10

    elif 150 <= word_count < 250:
        score += 6

    elif word_count > 900:
        score += 5

    return min(score, 100)


def generate_suggestions(
    text,
    detected_skills,
    missing_skills,
    detected_sections,
    missing_sections
):

    suggestions = []

    if not detect_email(text):
        suggestions.append(
            "Add a professional email address."
        )

    if not detect_phone(text):
        suggestions.append(
            "Add a valid phone number."
        )

    if not detect_linkedin(text):
        suggestions.append(
            "Add your LinkedIn profile URL."
        )

    if not detect_github(text):
        suggestions.append(
            "Add your GitHub profile, especially for software roles."
        )

    if "Summary" in missing_sections:
        suggestions.append(
            "Add a concise professional summary tailored to your target role."
        )

    if "Skills" in missing_sections:
        suggestions.append(
            "Create a dedicated technical skills section."
        )

    if "Projects" in missing_sections:
        suggestions.append(
            "Add a projects section with technologies and measurable outcomes."
        )

    if "Experience" in missing_sections:
        suggestions.append(
            "Add internships, freelance work, leadership, or relevant practical experience."
        )

    if count_action_verbs(text) < 4:
        suggestions.append(
            "Use stronger action verbs such as Developed, Built, Implemented, Optimized, and Led."
        )

    if count_metrics(text) < 2:
        suggestions.append(
            "Add measurable achievements using percentages, counts, performance gains, or scale."
        )

    if len(detected_skills) < 6:
        suggestions.append(
            "Strengthen your technical skills section with technologies you genuinely know."
        )

    if missing_skills:
        suggestions.append(
            "For general CSE placement readiness, consider strengthening: "
            + ", ".join(missing_skills[:6])
            + "."
        )

    word_count = len(text.split())

    if word_count < 200:
        suggestions.append(
            "The resume appears too brief. Add stronger project, internship, and achievement details."
        )

    elif word_count > 1000:
        suggestions.append(
            "The resume may be too long. Remove repetitive or low-impact content."
        )

    if not suggestions:
        suggestions.append(
            "Your resume has a strong baseline. Tailor keywords for each specific job description."
        )

    return suggestions


def analyze_resume(text):

    clean_text = normalize_text(text)

    detected_sections, missing_sections = detect_sections(
        clean_text
    )

    detected_skills = detect_skills(
        clean_text
    )

    missing_skills = detect_missing_skills(
        detected_skills
    )

    ats_score = calculate_ats_score(
        clean_text,
        detected_skills,
        detected_sections
    )

    suggestions = generate_suggestions(
        clean_text,
        detected_skills,
        missing_skills,
        detected_sections,
        missing_sections
    )

    return {
        "ats_score": ats_score,

        "detected_skills": detected_skills,

        "missing_skills": missing_skills,

        "detected_sections": detected_sections,

        "missing_sections": missing_sections,

        "suggestions": suggestions,

        "word_count": len(clean_text.split()),

        "has_email": detect_email(clean_text),

        "has_phone": detect_phone(clean_text),

        "has_linkedin": detect_linkedin(clean_text),

        "has_github": detect_github(clean_text),

        "action_verb_count": count_action_verbs(clean_text),

        "metric_count": count_metrics(clean_text)
    }