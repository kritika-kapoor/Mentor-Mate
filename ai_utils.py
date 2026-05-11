import re
import random
import json
import os
from groq import Groq



import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = "llama-3.1-8b-instant"

# ── Persistent question history ──────────────────────────────────────────────
HISTORY_FILE = "questions_history.json"

def _load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def _save_history(history):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except:
        pass

def _get_used_questions(key):
    history = _load_history()
    return history.get(key, [])

def _add_used_questions(key, questions):
    history = _load_history()
    existing = history.get(key, [])
    existing_lower = [q.lower().strip() for q in existing]
    for q in questions:
        if q.lower().strip() not in existing_lower:
            existing.append(q)
    history[key] = existing
    _save_history(history)

def _filter_new_questions(questions, used_questions):
    used_lower = [q.lower().strip() for q in used_questions]
    return [q for q in questions if q.lower().strip() not in used_lower]

def _remove_non_technical(questions):
    non_tech_triggers = [
        "stay updated", "motivate", "ensure quality", "responsibilities",
        "work ethic", "team environment", "communicate", "handle pressure",
        "career goal", "strength", "weakness", "introduce yourself",
        "why do you want", "where do you see", "tell me about yourself",
        "how do you work with", "what drives you", "passion", "hobby",
        "work life balance", "management style", "leadership style"
    ]
    clean = []
    for q in questions:
        q_lower = q.lower()
        if not any(trigger in q_lower for trigger in non_tech_triggers):
            clean.append(q)
    return clean


def call_groq(prompt: str) -> str:
    try:
        random_seed = random.randint(10000, 99999)
        varied_prompt = f"[UniqueSession:{random_seed}] {prompt}"
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict professional technical interviewer. Follow all instructions exactly. Never add extra text, headings, or explanations. Only output the questions. CRITICAL: Generate completely FRESH and UNIQUE questions every single time. Never repeat the same questions from previous sessions."
                },
                {
                    "role": "user",
                    "content": varied_prompt
                }
            ],
            temperature=1.2,
            max_tokens=1500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"


def _clean_questions(raw_output, count, fallback):
    if raw_output.startswith("ERROR:") or len(raw_output.strip()) < 20:
        random.shuffle(fallback)
        return fallback[:count]

    questions = []
    for line in raw_output.split("\n"):
        clean = line.strip()
        clean = re.sub(r"^[-*•\s]+", "", clean)
        clean = re.sub(r"^\d+[\).\s-]*", "", clean)
        clean = clean.replace("**", "")
        clean = re.sub(r"\s+", " ", clean).strip()
        if len(clean) < 10:
            continue
        if not clean.endswith("?"):
            clean += "?"
        questions.append(clean)

    if len(questions) < 3:
        random.shuffle(fallback)
        return fallback[:count]

    return questions[:count]


# ================= RESUME ROUND =================
def generate_resume_questions(job_role, resume_data, difficulty):
    skills_list = resume_data.get("skills", [])
    projects_list = resume_data.get("projects", [])

    skills = ", ".join(skills_list) if skills_list else "programming, data structures"
    projects = " | ".join(projects_list[:4]) if projects_list else "software project"
    sample_skills = random.sample(skills_list, min(3, len(skills_list))) if skills_list else ["programming"]

    history_key = f"resume_{job_role}_{difficulty}".lower().replace(" ", "_")
    used_questions = _get_used_questions(history_key)

    depth = {
        "Easy": "Ask only very basic definitions and simple concept questions a beginner can answer. Example: What is a variable? What is a function? What is OOPs? What is a linked list?",
        "Medium": "Ask how-to and implementation questions. Example: How does a hash map work internally? How do you handle memory leaks in C++? What is the difference between stack and heap?",
        "Hard": "Ask deep optimization, design and problem-solving questions. Example: How would you optimize a recursive function using dynamic programming? What are the tradeoffs between different sorting algorithms?"
    }.get(difficulty, "Ask medium level questions.")

    variety_words = random.choice([
        "Focus on practical real-world scenarios.",
        "Focus on edge cases and problem solving.",
        "Focus on core fundamentals and theory.",
        "Focus on coding and implementation details.",
        "Focus on system design and architecture.",
        "Focus on debugging and troubleshooting.",
        "Focus on comparisons between different approaches.",
        "Focus on best practices and industry standards.",
    ])

    avoid_str = ""
    if used_questions:
        sample_avoid = used_questions[-20:]
        avoid_str = "\n\nDo NOT ask any of these previously used questions:\n" + "\n".join(f"- {q}" for q in sample_avoid)

    prompt = f"""You are interviewing a candidate for the role of {job_role}.

Candidate skills: {skills}
Candidate projects: {projects}
Difficulty: {difficulty}
Special focus this session: {variety_words}
{avoid_str}

TASK: Generate exactly 15 UNIQUE interview questions. Mix up question styles.

- Questions 1 to 12: Pure technical questions on skills ({skills}). Difficulty: {difficulty} — {depth}. Do NOT mention projects.
- Questions 13 to 15: Questions about the candidate's projects ({projects}).

OUTPUT FORMAT:
- One question per line
- No numbering, no bullets, no headings
- End each question with ?
- Output only the 15 questions, nothing else"""

    fallback = [
        f"What is the difference between a stack and a queue in {sample_skills[0]}?",
        f"How does memory management work in {sample_skills[0]}?",
        f"Explain the concept of inheritance in OOPs with an example?",
        f"What is the time complexity of binary search and why?",
        f"How do you handle exceptions in {sample_skills[0]}?",
        f"What is a pointer and how is it different from a reference?",
        f"Explain the difference between primary key and foreign key in MySQL?",
        f"What are the SOLID principles in object-oriented design?",
        f"How does a hash table work internally?",
        f"What is the difference between process and thread?",
        f"How do you optimize a slow SQL query?",
        f"What is the difference between compile time and runtime errors?",
        f"What was the main technical challenge you faced in your {projects.split('|')[0].strip()} project?",
        f"What data structures did you use in your project and why?",
        f"How did you test and debug your project?"
    ]

    raw = call_groq(prompt)
    hr_triggers = ["tell me about yourself", "why do you want", "strength", "weakness",
                   "motivate", "salary", "hire you", "introduce yourself", "dream job"]
    if any(t in raw.lower() for t in hr_triggers):
        result = fallback[:15]
        _add_used_questions(history_key, result)
        return result

    result = _clean_questions(raw, 15, fallback)
    new_result = _filter_new_questions(result, used_questions)

    if len(new_result) < 10:
        raw2 = call_groq(prompt)
        result2 = _clean_questions(raw2, 15, fallback)
        new_result = _filter_new_questions(result2, used_questions)

    final = (new_result + result)[:15]
    _add_used_questions(history_key, final)
    return final


# ================= JOB ROLE ROUND =================
def generate_job_role_questions(job_role, difficulty):
    history_key = f"jobrole_{job_role}_{difficulty}".lower().replace(" ", "_")
    used_questions = _get_used_questions(history_key)

    depth = {
        "Easy": "Ask only very basic fresher-level questions about simple definitions, tools and concepts answerable by someone with zero experience. Example: What is a pivot table? What does SQL stand for? What is Python used for?",
        "Medium": "Ask practical working-level questions about real scenarios. Example: How would you handle missing values in a dataset? How do you write a SQL query to find duplicate records? What is the difference between inner join and left join?",
        "Hard": "Ask advanced senior-level questions about architecture, optimization and complex problem solving. Example: How would you design a data pipeline for real-time analytics? How do you optimize a query joining 5 large tables?"
    }.get(difficulty, "Ask medium level questions.")

    variety_words = random.choice([
        "Focus on practical real-world technical scenarios.",
        "Focus on tools and technologies used daily.",
        "Focus on technical problem solving and edge cases.",
        "Focus on system design and architecture.",
        "Focus on debugging and troubleshooting techniques.",
        "Focus on performance and optimization.",
        "Focus on technical best practices and standards.",
        "Focus on comparisons between technical approaches.",
    ])

    avoid_str = ""
    if used_questions:
        sample_avoid = used_questions[-20:]
        avoid_str = "\n\nDo NOT ask any of these previously used questions:\n" + "\n".join(f"- {q}" for q in sample_avoid)

    prompt = f"""You are a senior interviewer at a top tech company hiring for the role: {job_role}.

Difficulty: {difficulty}
Instruction: {depth}
Special focus this session: {variety_words}
{avoid_str}

TASK: Generate exactly 15 PURELY TECHNICAL interview questions for the {job_role} role.

STRICT RULES:
- Every single question must be 100% technical — about code, tools, algorithms, systems, databases, concepts
- Questions like "How do you stay updated?" or "What motivates you?" are BANNED — these are HR questions not technical
- Questions must test actual technical knowledge and skills only
- Must be completely different from all previously asked questions
- Match difficulty level exactly: {difficulty}
- Do NOT ask about projects, soft skills, motivation, career goals, teamwork
- One question per line, no numbering, no bullets, no headings
- End each question with ?
- Output only the 15 questions, nothing else
- You MUST output all 15 questions. Do not stop before question 15.

GOOD examples: {depth}
BAD examples (NEVER ask): How do you stay updated? What motivates you? How do you ensure quality? What are your responsibilities? How do you work in a team?"""

    fallback = [
        f"What is the difference between supervised and unsupervised learning?",
        f"Explain how a binary search tree works?",
        f"What is the difference between SQL JOIN types — INNER, LEFT, RIGHT, FULL?",
        f"How does indexing improve database query performance?",
        f"What is the difference between a list and a tuple in Python?",
        f"Explain the concept of normalization in databases?",
        f"What is Big O notation and why is it important?",
        f"What is the difference between GET and POST HTTP methods?",
        f"Explain how a hash map works internally?",
        f"What is the difference between stack memory and heap memory?",
        f"What is a foreign key constraint in SQL?",
        f"How does a REST API work?",
        f"What is the difference between a process and a thread?",
        f"Explain what recursion is and give an example?",
        f"What is the time complexity of quicksort in the worst case?"
    ]

    result = _clean_questions(call_groq(prompt), 15, fallback)
    result = _remove_non_technical(result)
    new_result = _filter_new_questions(result, used_questions)

    if len(new_result) < 10:
        result2 = _clean_questions(call_groq(prompt), 15, fallback)
        result2 = _remove_non_technical(result2)
        new_result = _filter_new_questions(result2, used_questions)

    if len(new_result) < 10:
        new_result = _filter_new_questions(fallback, used_questions)

    final = (new_result + fallback)[:15]
    _add_used_questions(history_key, final)
    return final


# ================= HR ROUND =================
def generate_hr_questions(job_role, difficulty):
    history_key = f"hr_{job_role}_{difficulty}".lower().replace(" ", "_")
    used_questions = _get_used_questions(history_key)

    depth = {
        "Easy": "Ask very simple, friendly, basic questions a fresher can answer. Example: Tell me about yourself. What are your hobbies? Why did you choose this field? What do you like about working in a team?",
        "Medium": "Ask situational and behavioral questions. Example: Tell me about a time you handled a difficult situation. How do you manage your time when handling multiple tasks? Describe a situation where you disagreed with someone.",
        "Hard": "Ask deep leadership and pressure-handling questions. Example: Describe a time you completely failed and what you did about it. How do you handle a team member who is consistently underperforming? Tell me about a time you had to make a difficult decision with incomplete information."
    }.get(difficulty, "Ask medium level questions.")

    variety_words = random.choice([
        "Focus on teamwork and collaboration scenarios.",
        "Focus on handling conflicts and pressure.",
        "Focus on career goals and self-awareness.",
        "Focus on communication and leadership.",
        "Focus on adaptability and learning from failure.",
        "Focus on motivation and work ethic.",
        "Focus on time management and prioritization.",
        "Focus on creativity and problem solving attitude.",
    ])

    avoid_str = ""
    if used_questions:
        sample_avoid = used_questions[-15:]
        avoid_str = "\n\nDo NOT ask any of these previously used questions:\n" + "\n".join(f"- {q}" for q in sample_avoid)

    prompt = f"""You are an HR interviewer at a company hiring for: {job_role}.

Difficulty: {difficulty}
Instruction: {depth}
Special focus this session: {variety_words}
{avoid_str}

TASK: Generate exactly 10 FRESH and UNIQUE behavioral HR interview questions.

Rules:
- Questions must be about personality, teamwork, communication, goals, work ethic, leadership
- Must be completely different from all previously asked questions
- Do NOT ask any technical questions
- Match difficulty level strictly: {difficulty} — {depth}
- One question per line, no numbering, no bullets, no headings
- End each question with ?
- Output only the 10 questions, nothing else"""

    fallback = [
        "Tell me about yourself?",
        f"Why do you want to work as a {job_role}?",
        "Why should we hire you?",
        "What are your greatest strengths?",
        "What is your biggest weakness and how are you working on it?",
        "Where do you see yourself in 5 years?",
        "Tell me about a challenge you faced and how you overcame it?",
        "How do you handle pressure and tight deadlines?",
        "How do you work in a team environment?",
        "What motivates you to perform your best?"
    ]

    result = _clean_questions(call_groq(prompt), 10, fallback)
    new_result = _filter_new_questions(result, used_questions)

    if len(new_result) < 7:
        result2 = _clean_questions(call_groq(prompt), 10, fallback)
        new_result = _filter_new_questions(result2, used_questions)

    final = (new_result + result)[:10]
    _add_used_questions(history_key, final)
    return final