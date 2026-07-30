import os
import sys

# Paths
source_app = r"c:\Users\pamug\Downloads\career zip\project 1\app.py"
source_improvements = r"c:\Users\pamug\Downloads\career zip\project 1\improved_job_fields.py"
target_file = r"c:\Users\pamug\careerforge\routes\jobs_data.py"

# Read source files
with open(source_app, "r", encoding="utf-8") as f:
    app_content = f.read()

with open(source_improvements, "r", encoding="utf-8") as f:
    improvements_content = f.read()

# Extract SECTORS definition string from app.py
sectors_start = app_content.find("SECTORS = {")
sectors_end = app_content.find("\n\ndef ", sectors_start)
if sectors_end == -1:
    sectors_end = app_content.find("\n# ", sectors_start)

sectors_code = app_content[sectors_start:sectors_end].strip()

# Build the complete jobs_data.py
jobs_data_code = f'''"""
CareerForge — Job Search Data & Helper Module (Phase 1)
Contains in-memory curated sectors, job listings, recommendations, and search helpers.
"""

import os
import re
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

{improvements_content}

{sectors_code}

# ---------------------------------------------------------
# Data Helpers (In-Memory, zero SQLite dependency)
# ---------------------------------------------------------

def apply_improvements(job):
    if not isinstance(job, dict):
        return job
    j = dict(job)
    slug = j.get("slug", "")
    sector_key = j.get("sector_key", "")
    
    # 1. Exact slug overrides
    if slug in IMPROVED_JOB_FIELDS:
        j.update(IMPROVED_JOB_FIELDS[slug])
        return j

    # 2. Sector defaults fallback
    sec_defs = SECTOR_DEFAULTS.get(sector_key, {})
    for key, val in sec_defs.items():
        if not j.get(key) or j.get(key) in ["Check official notification", "As per notification", ""]:
            j[key] = val
    return j

def get_sectors():
    """Return a deep copy of sectors with improvements applied."""
    result = {{}}
    for sector_key, sector_data in SECTORS.items():
        sec = {{
            "title": sector_data.get("title", sector_key),
            "emoji": sector_data.get("emoji", "📁"),
            "jobs": [],
            "departments": {{}}
        }}
        
        # Sector-level jobs
        for job in sector_data.get("jobs", []):
            j = dict(job)
            j["sector_key"] = sector_key
            sec["jobs"].append(apply_improvements(j))
            
        # Department-level jobs
        if "departments" in sector_data:
            for dept_key, dept_data in sector_data.get("departments", {{}}).items():
                dept_jobs = []
                for job in dept_data.get("jobs", []):
                    j = dict(job)
                    j["sector_key"] = sector_key
                    j["department_key"] = dept_key
                    dept_jobs.append(apply_improvements(j))
                sec["departments"][dept_key] = {{
                    "title": dept_data.get("title", dept_key),
                    "emoji": dept_data.get("emoji", "📂"),
                    "jobs": dept_jobs
                }}
                
        result[sector_key] = sec
    return result

def get_sector(sector_key):
    return get_sectors().get(sector_key)

def get_all_jobs():
    jobs = []
    for sector_key, sector in get_sectors().items():
        for job in sector.get("jobs", []):
            jobs.append(job)
        for dept in sector.get("departments", {{}}).values():
            for job in dept.get("jobs", []):
                jobs.append(job)
    return sorted(jobs, key=lambda x: x.get("title", "").lower())

def get_job_by_slug(slug):
    for job in get_all_jobs():
        if job.get("slug") == slug:
            return job
    return None

def find_job_by_slug(sector_key, slug):
    for job in get_all_jobs():
        if job.get("slug") == slug and job.get("sector_key") == sector_key:
            return job
    return get_job_by_slug(slug)

def get_departments_for_sector(sector_key):
    sec = get_sector(sector_key)
    if sec:
        return sec.get("departments", {{}})
    return {{}}

def get_portal_stats():
    jobs = get_all_jobs()
    sectors = get_sectors()
    departments_count = sum(len(sec.get("departments", {{}})) for sec in sectors.values())
    govt_jobs = sum(1 for job in jobs if job.get("sector_key") in ["state", "central"])
    return {{
        "jobs_count": len(jobs),
        "sectors_count": len(sectors),
        "departments_count": departments_count,
        "govt_jobs_count": govt_jobs,
    }}

def get_daily_job_spotlight():
    jobs = get_all_jobs()
    if not jobs:
        return None
    jobs = sorted(jobs, key=lambda j: (str(j.get("title", "")), str(j.get("slug", ""))))
    day_bucket = int(datetime.now(timezone.utc).timestamp() // 86400)
    job = dict(jobs[day_bucket % len(jobs)])
    title = job.get("title", "this career")
    skills = job.get("skills") or job.get("skill") or "the core skills listed in this career profile"
    degree = job.get("degree") or job.get("qualification") or "the required qualification"
    job["spotlight_text"] = (
        f"Do you know? To become a {{title}}, you need to ace skills such as {{skills}}. "
        f"Check the eligibility details and career path for the required qualification: {{degree}}."
    )
    job["spotlight_bucket"] = day_bucket
    return job

# ---------------------------------------------------------
# Eligibility & Recommendation Logic
# ---------------------------------------------------------

def job_matches_degree(job, degree_text):
    if not degree_text:
        return True
    degree_text = degree_text.lower().strip()
    haystack = (str(job.get("degree", "")) + " " + str(job.get("title", "")) + " " + str(job.get("skills", ""))).lower()
    keywords = {{
        "btech": ["b.tech", "btech", "engineering", "be ", "b.e", "diploma"],
        "degree": ["graduate", "any graduate", "degree", "b.sc", "b.com", "b.a"],
        "intermediate": ["intermediate", "12th", "10+2", "pass"],
        "diploma": ["diploma", "iti", "polytechnic"],
        "any": ["any", "graduate", "pass", "diploma", "b.tech", "b.sc"],
    }}
    selected = keywords.get(degree_text, [degree_text])
    return any(k in haystack for k in selected)

def job_matches_age(job, age_value):
    if not age_value:
        return True
    try:
        age = int(age_value)
    except ValueError:
        return True
    ages = [int(x) for x in re.findall(r"\\d+", str(job.get("age", "")))]
    if len(ages) >= 2:
        return min(ages) <= age <= max(ages)
    return True

def recommend_jobs(profile):
    jobs = get_all_jobs()
    scored = []
    degree = profile.get("degree", "").lower()
    skills = [x.strip().lower() for x in profile.get("skills", "").replace(";", ",").split(",") if x.strip()]
    interest = profile.get("interest", "").lower()
    age = profile.get("age", "")

    for job in jobs:
        score = 0
        reasons = []
        haystack = " ".join([
            str(job.get("title", "")), str(job.get("degree", "")), str(job.get("skills", "")),
            str(job.get("full_description", "")), str(job.get("sector_key", ""))
        ]).lower()

        if degree and job_matches_degree(job, degree):
            score += 35
            reasons.append("education match")
        if age and job_matches_age(job, age):
            score += 15
            reasons.append("age range suitable")
        matched_skills = [skill for skill in skills if skill and skill in haystack]
        if matched_skills:
            score += min(30, len(matched_skills) * 10)
            reasons.append("skills: " + ", ".join(matched_skills[:3]))
        if interest and interest in haystack:
            score += 20
            reasons.append("interest match")
        if not degree and not skills and not interest:
            score = 10
            reasons.append("general recommendation")

        if score > 0:
            scored.append({{"job": job, "score": min(score, 100), "reasons": reasons}})

    return sorted(scored, key=lambda x: x["score"], reverse=True)[:12]

# ---------------------------------------------------------
# Live Jobs & API Integration
# ---------------------------------------------------------

def _strip_html(value):
    if not value:
        return ""
    return re.sub(r"<[^>]+>", " ", str(value)).replace("&nbsp;", " ").strip()

def _company_initials(name):
    clean = str(name or "Job").replace(",", " ").replace(".", " ").strip()
    parts = [p for p in clean.split() if p and p.lower() not in ["inc", "ltd", "llc", "pvt", "company", "corp"]]
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return (parts[0][:2] if parts else "JB").upper()

def _clean_live_salary(value):
    raw = str(value or "").strip()
    if not raw or raw.lower() in ["none", "null", "false", "n/a", "na"]:
        return "As per company standards"
    low = raw.lower()
    m = re.fullmatch(r"\\$?\\s*(\\d+(?:\\.\\d+)?)\\s*[kK]", raw)
    if m:
        amount = float(m.group(1)) * 1000
        return "USD {{:,.0f}}/year".format(amount)
    if raw.startswith("$") and "/" not in raw and "year" not in low and "month" not in low:
        return raw.replace("$", "USD ", 1) + "/year"
    return raw

def _norm_location_text(value):
    text = str(value or "").lower().strip()
    fixes = {{"guntue": "guntur", "gunture": "guntur", "guntur,": "guntur"}}
    for wrong, right in fixes.items():
        text = text.replace(wrong, right)
    return text

def _location_matches(job, location):
    raw = _norm_location_text(location)
    if not raw:
        return True
    first = raw.split(",")[0].strip()
    loc = first or raw
    job_location = _norm_location_text(job.get("location", ""))
    job_text = _norm_location_text(" ".join(str(job.get(k, "")) for k in ["location", "title", "company", "skills", "source", "badge"]))

    remote_words = ["remote", "worldwide", "anywhere", "global", "work from home", "wfh"]
    india_cities = ["hyderabad", "bengaluru", "bangalore", "chennai", "pune", "mumbai", "delhi", "gurgaon", "gurugram", "noida", "guntur", "vijayawada", "visakhapatnam", "vizag", "kolkata", "ahmedabad"]

    if loc in ["remote", "worldwide", "global", "wfh", "work from home"]:
        return any(w in job_text for w in remote_words)
    if loc in ["india", "in"]:
        return "india" in job_text or any(city in job_location for city in india_cities)
    return loc in job_location

def _json_get(url, timeout=5):
    try:
        req = urllib.request.Request(url, headers={{"User-Agent": "CareerForge/1.0"}})
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return json.loads(res.read().decode("utf-8", errors="ignore"))
    except Exception:
        return None

def fetch_remotive_jobs(keyword="software", location="", limit=18):
    query = keyword or "software"
    url = "https://remotive.com/api/remote-jobs?" + urllib.parse.urlencode({{"search": query}})
    data = _json_get(url) or {{}}
    jobs = []
    for item in data.get("jobs", [])[:limit * 3]:
        job_location = item.get("candidate_required_location") or "Remote / Worldwide"
        if location and location.lower() not in ["remote", "worldwide", "global", "india"] and "remote" not in location.lower():
            continue
        if location and location.lower() == "india" and "india" not in job_location.lower() and "worldwide" not in job_location.lower() and "anywhere" not in job_location.lower():
            continue
        jobs.append({{
            "source": "Worldwide Remote API",
            "badge": "REMOTE",
            "remote_flag": True,
            "title": item.get("title") or "Live Job Opening",
            "company": item.get("company_name") or "Hiring Company",
            "location": job_location,
            "salary": _clean_live_salary(item.get("salary")),
            "experience": "Fresher / Experienced",
            "qualification": "Relevant degree / portfolio / skills",
            "skills": item.get("tags") and ", ".join(item.get("tags")[:6]) or _strip_html(item.get("description"))[:90] or "Role-specific skills",
            "posted_at": item.get("publication_date", "Recently posted")[:10],
            "apply_url": item.get("url") or "#",
            "primary_organization": item.get("company_name") or "Remote Hiring Company",
            "official_board": "Company Careers / Remote Job Board",
            "official_portal": item.get("url") or "#",
            "roadmap": "Strengthen portfolio → Apply online → Interview → Remote onboarding → Career growth",
            "portal_slug": "",
            "sector_key": "",
            "department_key": ""
        }})
        if len(jobs) >= limit:
            break
    return jobs

def fetch_adzuna_jobs(keyword="software", location="India", limit=18):
    app_id = os.environ.get("ADZUNA_APP_ID", "").strip()
    app_key = os.environ.get("ADZUNA_APP_KEY", "").strip()
    if not app_id or not app_key:
        return []
    params = urllib.parse.urlencode({{
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": limit * 2,
        "what": keyword or "software",
        "where": location or "India",
        "content-type": "application/json"
    }})
    data = _json_get("https://api.adzuna.com/v1/api/jobs/in/search/1?" + params) or {{}}
    jobs = []
    for item in data.get("results", []):
        salary = "As per company standards"
        if item.get("salary_min") or item.get("salary_max"):
            salary = "₹{{:,.0f}} - ₹{{:,.0f}}/year".format(float(item.get("salary_min") or 0), float(item.get("salary_max") or 0))
        job = {{
            "source": "India Live API",
            "badge": "LIVE",
            "remote_flag": False,
            "title": item.get("title") or "Live Job Opening",
            "company": (item.get("company") or {{}}).get("display_name") or "Hiring Company",
            "location": (item.get("location") or {{}}).get("display_name") or location or "India",
            "salary": salary,
            "experience": "As per employer requirements",
            "qualification": "Relevant qualification / skills",
            "skills": _strip_html(item.get("description"))[:140] or "Check official job description",
            "posted_at": item.get("created", "Recently posted")[:10],
            "apply_url": item.get("redirect_url") or "#",
            "primary_organization": (item.get("company") or {{}}).get("display_name") or "Hiring Company",
            "official_board": "Company Careers / Adzuna India",
            "official_portal": item.get("redirect_url") or "#",
            "roadmap": "Check eligibility → Apply online → Screening → Interview → Offer",
            "portal_slug": "",
            "sector_key": "",
            "department_key": ""
        }}
        if _location_matches(job, location):
            jobs.append(job)
        if len(jobs) >= limit:
            break
    return jobs

def curated_india_live_jobs(keyword="", location="", limit=60):
    base_jobs = [
        ("Python Developer", "TCS", "Hyderabad, India", "₹4 - ₹8 LPA", "B.Tech / MCA", "Python, Flask, SQL, Git", "https://www.tcs.com/careers"),
        ("Graduate Engineer Trainee", "Infosys", "Bengaluru, India", "₹3.6 - ₹6 LPA", "B.Tech / BE", "Java, Python, Communication", "https://www.infosys.com/careers"),
        ("Data Analyst", "Accenture", "Pune, India", "₹4 - ₹7 LPA", "Any Graduate / B.Tech", "Excel, SQL, Power BI, Python", "https://www.accenture.com/in-en/careers"),
        ("Software Engineer", "Wipro", "Chennai, India", "₹3.5 - ₹7 LPA", "B.Tech / MCA", "Java, SQL, Testing", "https://careers.wipro.com"),
        ("Associate System Engineer", "IBM", "Bengaluru, India", "₹4 - ₹8 LPA", "B.Tech / MCA", "Cloud, Python, Linux, SQL", "https://www.ibm.com/careers/in-en"),
        ("Junior Web Developer", "HCLTech", "Noida, India", "₹3 - ₹6 LPA", "B.Tech / BCA / MCA", "HTML, CSS, JS, React", "https://www.hcltech.com/careers"),
        ("Cloud Support Associate", "Amazon", "Hyderabad, India", "₹5 - ₹10 LPA", "Any Graduate / B.Tech", "AWS, Linux, Networking", "https://www.amazon.jobs"),
        ("Business Analyst Trainee", "Deloitte", "Gurugram, India", "₹5 - ₹9 LPA", "B.Tech / BBA / MBA", "Analytics, Excel, SQL", "https://www2.deloitte.com/in/en/careers"),
        ("Cyber Security Analyst", "Tech Mahindra", "Mumbai, India", "₹4 - ₹8 LPA", "B.Tech CSE / IT", "Security, SIEM, Networking", "https://www.techmahindra.com/en-in/careers"),
        ("Software Test Engineer", "Capgemini", "Kolkata, India", "₹3.5 - ₹6.5 LPA", "B.Tech / MCA", "Manual Testing, Selenium, SQL", "https://www.capgemini.com/in-en/careers"),
        ("AI/ML Intern", "Startup India Network", "Remote / India", "Stipend / As per company", "B.Tech / Any Graduate", "Python, ML, Pandas, Projects", "https://www.startupindia.gov.in"),
        ("Python Remote Intern", "Indian Remote Startup", "Remote / India", "Stipend / As per company", "Student / Fresher", "Python, Flask, APIs, Git", "https://internshala.com/internships/python-development-internship"),
        ("Banking Associate", "HDFC Bank", "Mumbai, India", "₹3 - ₹6 LPA", "Any Graduate", "Banking, Sales, Communication", "https://www.hdfcbank.com/personal/about-us/careers"),
        ("Probationary Officer", "IBPS Banks", "India", "As per bank pay scale", "Any Graduate", "Aptitude, Reasoning, Banking Awareness", "https://www.ibps.in"),
        ("Junior Assistant", "SSC / Central Govt", "India", "As per 7th CPC", "Intermediate / Graduate", "Typing, Reasoning, GK", "https://ssc.gov.in"),
        ("Railway Technician", "Railway Recruitment Board", "India", "As per RRB notification", "ITI / Diploma", "Technical, Aptitude, Safety", "https://www.rrbcdg.gov.in"),
        ("Project Assistant", "ISRO", "Bengaluru, India", "As per notification", "B.Tech / M.Sc", "Research, Python, Electronics", "https://www.isro.gov.in/Careers.html"),
        ("Graduate Apprentice", "DRDO", "Hyderabad, India", "Stipend as per rules", "B.Tech / Diploma", "Engineering basics, Documentation", "https://www.drdo.gov.in/drdo/careers"),
        ("Customer Support Executive", "Teleperformance", "Gurugram, India", "₹2.5 - ₹4.5 LPA", "Any Graduate", "Communication, CRM, Email", "https://www.teleperformance.com/en-us/careers"),
        ("Digital Marketing Executive", "Zoho Partner Network", "Chennai, India", "₹3 - ₹6 LPA", "Any Graduate", "SEO, Content, Analytics", "https://www.zoho.com/careers"),
        ("Frontend Developer", "Freshworks", "Chennai, India", "₹5 - ₹10 LPA", "B.Tech / MCA", "HTML, CSS, JavaScript, React", "https://www.freshworks.com/company/careers"),
        ("Backend Developer", "Razorpay", "Bengaluru, India", "₹8 - ₹16 LPA", "B.Tech / MCA", "Python, Java, APIs, SQL", "https://razorpay.com/jobs"),
        ("Data Engineer", "Cognizant", "Hyderabad, India", "₹5 - ₹11 LPA", "B.Tech / MCA", "SQL, Python, ETL, Cloud", "https://careers.cognizant.com/india-en"),
        ("Technical Support Engineer", "Microsoft", "Bengaluru, India", "₹6 - ₹12 LPA", "B.Tech / Any Graduate", "Azure, Support, Networking", "https://careers.microsoft.com"),
        ("Android Developer", "Paytm", "Noida, India", "₹5 - ₹12 LPA", "B.Tech / MCA", "Android, Kotlin, Java", "https://paytm.com/careers"),
        ("Operations Associate", "Flipkart", "Bengaluru, India", "₹3 - ₹6 LPA", "Any Graduate", "Excel, Logistics, Coordination", "https://www.flipkartcareers.com"),
        ("HR Recruiter", "Naukri Employer Services", "Noida, India", "₹3 - ₹5 LPA", "Any Graduate / MBA", "Recruitment, HR, Communication", "https://www.naukri.com/careers"),
        ("Content Writer", "Education Technology Company", "Remote / India", "₹2.5 - ₹5 LPA", "Any Graduate", "Writing, Research, SEO", "https://www.linkedin.com/jobs"),
        ("Healthcare Data Executive", "Apollo Hospitals", "Hyderabad, India", "₹3 - ₹6 LPA", "Life Sciences / Any Graduate", "Excel, Healthcare, Data Entry", "https://www.apollohospitals.com/careers"),
        ("Education Counsellor", "BYJU'S / EdTech", "Bengaluru, India", "₹3 - ₹7 LPA", "Any Graduate", "Counselling, Sales, Communication", "https://byjus.com/careers"),
        ("IT Support Executive", "Local IT Services", "Guntur, India", "₹2.4 - ₹4.5 LPA", "Diploma / B.Tech / BCA", "Hardware, Networking, Windows", "https://www.ncs.gov.in"),
        ("Junior Python Developer", "Guntur Software Services", "Guntur, India", "₹3 - ₹5 LPA", "B.Tech / BCA / MCA", "Python, Django, SQL", "https://www.ncs.gov.in"),
        ("Data Entry Operator", "AP Local Services", "Guntur, India", "₹1.8 - ₹3 LPA", "Intermediate / Any Graduate", "Typing, Excel, Documentation", "https://www.apcfss.in"),
        ("Web Development Intern", "Vijayawada Tech Hub", "Vijayawada, India", "Stipend / Internship", "Student / Fresher", "HTML, CSS, JavaScript", "https://internshala.com"),
        ("Trainee Analyst", "Vizag IT Services", "Visakhapatnam, India", "₹3 - ₹5 LPA", "Any Graduate / B.Tech", "Excel, SQL, Reports", "https://www.ncs.gov.in"),
    ]
    key = (keyword or "").strip().lower()
    loc = (location or "").strip().lower()
    jobs = []
    for idx, (title, company, job_location, salary, qualification, skills, apply_url) in enumerate(base_jobs):
        item = {{
            "source": "India Curated Live Feed",
            "badge": "LIVE",
            "display_badge": "LIVE",
            "remote_flag": "remote" in job_location.lower(),
            "title": title,
            "company": company,
            "location": job_location,
            "salary": salary,
            "experience": "Fresher / Experienced",
            "qualification": qualification,
            "skills": skills,
            "posted_at": "Recently updated",
            "apply_url": apply_url,
            "primary_organization": company,
            "official_board": "Official Careers / Recruitment Portal",
            "official_portal": apply_url,
            "roadmap": "Check eligibility → Build required skills → Apply online → Interview / exam → Selection → Career growth",
            "portal_slug": "",
            "sector_key": "",
            "department_key": "",
            "company_initials": _company_initials(company),
            "ai_match": min(82 + ((idx * 3) % 15), 98),
        }}
        text = " ".join([title, company, job_location, qualification, skills]).lower()
        if key and key not in text:
            continue
        if loc and loc not in ["india", "in", ""] and not _location_matches(item, loc):
            continue
        jobs.append(item)
        if len(jobs) >= limit:
            break
    return jobs

def _merge_live_jobs(primary, fallback, limit=60):
    seen = set()
    merged = []
    for job in list(primary or []) + list(fallback or []):
        sig = ((job.get("title") or "").lower().strip(), (job.get("company") or "").lower().strip(), (job.get("location") or "").lower().strip())
        if sig in seen:
            continue
        seen.add(sig)
        merged.append(job)
        if len(merged) >= limit:
            break
    return merged

def build_portal_live_jobs(keyword="", location="", experience=""):
    portal_jobs = []
    key = (keyword or "").lower()
    exp = (experience or "").lower()
    for job in get_all_jobs():
        text = " ".join([job.get("title", ""), job.get("company_name", ""), job.get("job_location", ""), job.get("skills", ""), job.get("degree", ""), job.get("sector_key", ""), job.get("experience", "")]).lower()
        if key and key not in text:
            continue
        if exp and exp not in text and exp not in ["experienced", "remote"]:
            continue
        item = {{
            "source": "Portal Career Role",
            "badge": "PORTAL",
            "remote_flag": False,
            "title": job.get("title", "Untitled Job"),
            "company": job.get("company_name") or job.get("organization") or "Multiple recruiters",
            "location": job.get("job_location") or "As per notification",
            "salary": (job.get("pay", {{}}).get("A", {{}}) if isinstance(job.get("pay"), dict) else {{}}).get("annual", "As per notification"),
            "experience": job.get("experience") or "Fresher / Experienced",
            "qualification": job.get("degree") or "Check eligibility details",
            "skills": job.get("skills") or "Check job details",
            "posted_at": job.get("apply_dates") or "Career guidance role",
            "apply_url": job.get("apply_link") or "#",
            "primary_organization": job.get("company_name") or "Recruiting Organisation",
            "official_board": "Official Recruitment Portal",
            "official_portal": job.get("apply_link") or "#",
            "roadmap": job.get("roadmap") or job.get("career_growth") or "Build skills → Apply → Interview → Selection → Growth",
            "portal_slug": job.get("slug", ""),
            "sector_key": job.get("sector_key", ""),
            "department_key": job.get("department_key", "")
        }}
        if _location_matches(item, location):
            portal_jobs.append(item)
    return portal_jobs[:30]
'''

# Write script
os.makedirs(r"c:\Users\pamug\careerforge\scratch", exist_ok=True)
script_path = r"c:\Users\pamug\careerforge\scratch\gen_jobs_data.py"
with open(script_path, "w", encoding="utf-8") as f:
    f.write(jobs_data_code)

print("Extractor script written successfully.")
