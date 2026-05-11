import streamlit as st
import pdfplumber
import re
import spacy

EDUCATION_KEYWORDS = [
    "b.tech", "btech", "m.tech", "mtech", "bca", "mca",
    "b.sc", "msc", "bachelor", "master", "university", "college"
]

@st.cache_resource
def load_nlp():
    return spacy.load("en_core_web_sm")

def extract_resume_text(resume_file):
    text = ""
    with pdfplumber.open(resume_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else "Not found"

def extract_phone(text):
    match = re.search(r'(\+91[\-\s]?)?[6-9]\d{9}', text)
    return match.group(0) if match else "Not found"

def extract_skills(text):
    lines = text.splitlines()
    in_section = False
    section_lines = []

    skill_section_starters = [
        "technical skills", "skills", "core skills",
        "key skills", "technologies", "tech stack", "technical expertise"
    ]
    skill_section_enders = [
        "education", "projects", "experience", "internship",
        "achievements", "certifications", "objective", "summary",
        "career", "declaration", "awards", "curricular"
    ]

    for line in lines:
        stripped = line.strip().lower()
        clean = stripped.rstrip(':').strip()
        if not in_section:
            if clean in skill_section_starters:
                in_section = True
                continue
        else:
            if clean in skill_section_enders:
                break
            if stripped:
                section_lines.append(stripped)

    search_text = " ".join(section_lines) if section_lines else text.lower()

    skill_patterns = {
        "c++": r'c\+\+',
        "c": r'(?<!\w)c(?!\w)',
        "java": r'(?<!\w)java(?!\w)',
        "python": r'(?<!\w)python(?!\w)',
        "sql": r'(?<!\w)sql(?!\w)',
        "mysql": r'(?<!\w)mysql(?!\w)',
        "mongodb": r'(?<!\w)mongodb(?!\w)',
        "machine learning": r'machine learning',
        "deep learning": r'deep learning',
        "nlp": r'(?<!\w)nlp(?!\w)',
        "data analysis": r'data analysis',
        "data science": r'data science',
        "data structures": r'data structures',
        "algorithms": r'(?<!\w)algorithms(?!\w)',
        "oops": r'oops|object oriented',
        "file handling": r'file handling',
        "mern stack": r'mern stack|mern',
        "pandas": r'(?<!\w)pandas(?!\w)',
        "numpy": r'(?<!\w)numpy(?!\w)',
        "matplotlib": r'(?<!\w)matplotlib(?!\w)',
        "power bi": r'power bi',
        "tableau": r'(?<!\w)tableau(?!\w)',
        "excel": r'(?<!\w)excel(?!\w)',
        "streamlit": r'(?<!\w)streamlit(?!\w)',
        "flask": r'(?<!\w)flask(?!\w)',
        "fastapi": r'(?<!\w)fastapi(?!\w)',
        "html": r'(?<!\w)html(?!\w)',
        "css": r'(?<!\w)css(?!\w)',
        "javascript": r'(?<!\w)javascript(?!\w)',
        "react": r'(?<!\w)react(?!\w)',
        "node": r'(?<!\w)node(?!\w)',
        "express": r'(?<!\w)express(?!\w)',
        "git": r'(?<!\w)git(?!\w)',
        "github": r'(?<!\w)github(?!\w)',
        "tensorflow": r'(?<!\w)tensorflow(?!\w)',
        "keras": r'(?<!\w)keras(?!\w)',
        "pytorch": r'(?<!\w)pytorch(?!\w)',
        "scikit-learn": r'scikit-learn',
        "django": r'(?<!\w)django(?!\w)',
        "bootstrap": r'(?<!\w)bootstrap(?!\w)',
        "php": r'(?<!\w)php(?!\w)',
        "kotlin": r'(?<!\w)kotlin(?!\w)',
        "typescript": r'(?<!\w)typescript(?!\w)',
        "docker": r'(?<!\w)docker(?!\w)',
        "aws": r'(?<!\w)aws(?!\w)',
        "azure": r'(?<!\w)azure(?!\w)',
        "linux": r'(?<!\w)linux(?!\w)',
        "opencv": r'(?<!\w)opencv(?!\w)',
        "next.js": r'next\.js|nextjs',
        "vue": r'(?<!\w)vue(?!\w)',
        "angular": r'(?<!\w)angular(?!\w)',
        "firebase": r'(?<!\w)firebase(?!\w)',
        "postgres": r'postgresql|postgres',
        "sqlite": r'(?<!\w)sqlite(?!\w)',
        "c#": r'c#|c sharp',
        "matlab": r'(?<!\w)matlab(?!\w)'
    }

    found_skills = []
    for skill, pattern in skill_patterns.items():
        if re.search(pattern, search_text):
            found_skills.append(skill)

    return found_skills

def extract_education(text):
    text_lower = text.lower()
    found_education = []
    for edu in EDUCATION_KEYWORDS:
        if edu in text_lower:
            found_education.append(edu)
    return list(set(found_education))

def extract_named_entities(text, nlp):
    doc = nlp(text)
    entities = {"PERSON": [], "ORG": [], "GPE": []}
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    for key in entities:
        entities[key] = list(set(entities[key]))
    return entities

def _clean_project_line(line):
    line = re.sub(
        r'\s*[\|]?\s*(github[\s\-]*project\s*link|github[\s\-]*link|'
        r'live\s*demo|source\s*code|demo\s*link|view\s*project|'
        r'https?://\S+|www\.\S+)',
        '', line, flags=re.IGNORECASE
    )
    line = re.sub(r'[\|]\s*\w+\.?\s+\d{4}\s*[-]\s*\w+\.?\s+\d{4}', '', line)
    line = re.sub(r'\(\d{4}\s*[-]\s*\d{4}\)', '', line)
    line = re.sub(r'\s*\|\s*[A-Za-z].*$', '', line)
    return line.strip()

def _is_valid_project_title(line):
    """
    Returns True only if the line looks like a real project title.
    Rejects description lines using strict rules.
    """
    # Must not contain em-dash (—) — used in descriptions
    if '—' in line:
        return False
    # Must not end with a period — descriptions end with periods
    if line.endswith('.'):
        return False
    # Must not end with a comma
    if line.endswith(','):
        return False
    # Must start with a capital letter
    if not line[0].isupper():
        return False
    # Must be short enough — real titles are under 50 chars
    if len(line) > 50:
        return False
    # Must not contain more than 2 commas — descriptions have lists
    if line.count(',') > 2:
        return False
    # Must not be all lowercase words (sentence fragments)
    words = line.split()
    if len(words) > 2 and all(w[0].islower() for w in words if w[0].isalpha()):
        return False
    return True

def extract_projects(text):
    lines = text.splitlines()
    project_names = []
    project_section = False

    start_keywords = [
        "projects", "project", "academic projects", "personal projects",
        "key projects", "notable projects", "selected projects",
        "project work", "project experience", "major projects"
    ]

    stop_keywords = [
        "achievement", "activity", "activities", "curricular",
        "education", "qualification", "skill", "certification",
        "internship", "experience", "work history", "employment",
        "declaration", "reference", "objective", "summary", "profile",
        "award", "honor", "language", "hobby", "interest",
        "contact", "career", "volunteer", "publication", "training",
        "achievements", "achievement", "curricular", "activities"
    ]

    skip_patterns = [
        "skills applied", "tech stack", "technologies used", "tools used",
        "my learnings", "my role", "role:", "description:",
        "developed", "designed", "implemented", "built", "created",
        "the project", "this project", "it is", "it was", "it allows",
        "it provides", "used to", "aims to", "helps to", "enables",
        "allows users", "responsible for", "worked on", "contributed",
        "gained", "strengthened", "learnt", "learned", "understanding",
        "comprises", "comprising", "features include", "key features",
        "i handled", "our team", "as part of", "the system", "the app",
        "this system", "this app", "this web", "the web",
        "in real-world", "real world", "upon successful", "ticket upon",
        "file handling in", "data structures and", "modular programming",
        "data organization", "inventory management", "oops principles",
        "object oriented", "electronic ticket", "seamlessly",
        "web application", "admin panel", "user panel", "guide panel",
        "in one place", "user needs", "user engagement", "overall user",
        "aligns with", "connect with", "share and", "explore travel",
        "plan their", "all in one", "full-featured", "three-panel",
        "a backend", "the content", "real-time", "analyzing",
        "generating", "delivering", "performance feedback",
        "resume analysis", "evaluates", "improvement insights",
        "interview environment", "interview assistant",
    ]

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        lower_line = line_clean.lower()

        if not project_section:
            if any(lower_line == kw or lower_line == kw + ":" for kw in start_keywords):
                project_section = True
            continue

        if any(lower_line == kw or lower_line == kw + ":"
               or lower_line.startswith(kw + " ") or lower_line.startswith(kw + ":")
               or lower_line.startswith(kw + " &") or lower_line.startswith(kw + "&")
               for kw in stop_keywords):
            break

        if any(skip in lower_line for skip in skip_patterns):
            continue

        if re.match(r'^[\d\s\-/|.]+$', line_clean):
            continue

        if len(line_clean) < 4:
            continue

        cleaned = _clean_project_line(line_clean)

        if not cleaned or len(cleaned) < 4:
            continue

        cleaned = re.sub(r'^[\-\*\u2022\u25BA\u25AA\u25C6]\s*', '', cleaned)
        cleaned = re.sub(r'^\d+[\.\)]\s*', '', cleaned).strip()

        if not cleaned or len(cleaned) < 4:
            continue

        # ── KEY FIX: validate it looks like a real project title ──
        if not _is_valid_project_title(cleaned):
            continue

        if cleaned not in project_names:
            project_names.append(cleaned)

        if len(project_names) >= 5:
            break

    # Fallback 1: "Project Name: ..." label style
    if not project_names:
        for match in re.findall(r'(?:project\s*(?:name|title)?\s*[:\-])\s*(.+)', text, re.IGNORECASE):
            name = _clean_project_line(match.strip())
            if 4 < len(name) < 80 and name not in project_names:
                project_names.append(name)
            if len(project_names) >= 5:
                break

    # Fallback 2: Capitalized phrase before system/app/website/tool
    if not project_names:
        for match in re.findall(
            r'([A-Z][a-zA-Z0-9\s\-]{3,50}?)\s*(?:system|app|application|website|portal|tool|platform|bot|dashboard)',
            text
        ):
            name = match.strip()
            if len(name) > 4 and name not in project_names:
                project_names.append(name)
            if len(project_names) >= 5:
                break

    print("EXTRACTED PROJECT NAMES:", project_names)
    return project_names if project_names else ["Software Project"]

def analyze_resume(text, nlp):
    return {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "entities": extract_named_entities(text, nlp),
        "projects": extract_projects(text)
    }