import re
from ai_utils import call_groq as call_ollama
from helpers import clean_llm_visuals, extract_section

STOPWORDS = {
    "the", "is", "a", "an", "and", "or", "of", "to", "in", "for", "on", "with",
    "what", "how", "why", "when", "where", "which", "who", "whom", "this", "that",
    "these", "those", "are", "was", "were", "be", "being", "been", "do", "does",
    "did", "can", "could", "should", "would", "will", "about", "explain", "describe",
    "tell", "me", "your", "you", "it", "its", "from", "as", "at"
}

TECH_KEYWORDS = [
    "c", "c++", "java", "python", "sql", "mysql", "mongodb", "dbms",
    "oops", "os", "networking", "html", "css", "javascript", "react",
    "machine learning", "deep learning", "nlp", "data science"
]

def extract_keywords_for_relevance(text):
    text = text.lower()
    found = set()

    for kw in TECH_KEYWORDS:
        if re.search(rf'(?<!\w){re.escape(kw)}(?!\w)', text):
            found.add(kw)

    words = re.findall(r"[a-zA-Z]+(?:\+\+)?", text)
    for word in words:
        if len(word) > 2 and word not in STOPWORDS:
            found.add(word)

    return found

def is_answer_relevant(question, answer):
    q_keys = extract_keywords_for_relevance(question)
    a_keys = extract_keywords_for_relevance(answer)

    overlap = q_keys.intersection(a_keys)
    important_q = [kw for kw in TECH_KEYWORDS if kw in q_keys]

    if important_q:
        if not any(term in a_keys for term in important_q):
            return False

    if len(overlap) == 0:
        return False

    return True

def generate_ideal_answer_only(question, job_role):
    prompt = f"""
You are a professional interviewer.

Job Role: {job_role}
Question: {question}

Return exactly in this format:

Ideal Answer: <short and correct ideal answer>

Rules:
- No HTML
- No markdown
- No bullets
- Keep it concise but meaningful
- The answer must directly match the question
"""

    raw_output = call_ollama(prompt)

    if raw_output.startswith("ERROR:"):
        return "Could not generate ideal answer."

    raw_output = clean_llm_visuals(raw_output)
    ideal_answer = extract_section(raw_output, "Ideal Answer", [])

    if not ideal_answer:
        ideal_answer = raw_output.strip()

    if not ideal_answer:
        ideal_answer = "Could not generate ideal answer."

    return clean_llm_visuals(ideal_answer)

def evaluate_answer(question, answer, job_role):
    if not answer.strip() or answer.strip().lower() == "skipped":
        ideal_answer = generate_ideal_answer_only(question, job_role)
        return {
            "score": "0/10",
            "feedback": "No valid answer provided.",
            "missing_points": "The question was not answered.",
            "ideal_answer": ideal_answer
        }

    if not is_answer_relevant(question, answer):
        ideal_answer = generate_ideal_answer_only(question, job_role)
        return {
            "score": "0/10",
            "feedback": "The answer is not relevant to the question.",
            "missing_points": "You did not address the actual topic asked in the question.",
            "ideal_answer": ideal_answer
        }

    prompt = f"""
You are a very strict technical interviewer.

Job Role: {job_role}
Question: {question}
Candidate Answer: {answer}

RULES:
1. If answer is partially correct, give low score.
2. If answer lacks depth, reduce marks.
3. Do NOT give high marks for good English alone.
4. Be strict and realistic.

Return exactly:

Score: <score out of 10>
Feedback: <short feedback>
Missing Points: <short missing points>
Ideal Answer: <short ideal answer>
"""

    raw_output = call_ollama(prompt)

    if raw_output.startswith("ERROR:"):
        return {
            "score": "0/10",
            "feedback": raw_output,
            "missing_points": "Could not evaluate.",
            "ideal_answer": "Could not generate."
        }

    raw_output = clean_llm_visuals(raw_output)

    score = extract_section(raw_output, "Score", ["Feedback", "Missing Points", "Ideal Answer"])
    feedback = extract_section(raw_output, "Feedback", ["Missing Points", "Ideal Answer", "Score"])
    missing_points = extract_section(raw_output, "Missing Points", ["Ideal Answer", "Score", "Feedback"])
    ideal_answer = extract_section(raw_output, "Ideal Answer", [])

    if not score:
        score = "0/10"
    if not feedback:
        feedback = "Answer needs improvement."
    if not missing_points:
        missing_points = "More detailed explanation required."
    if not ideal_answer:
        ideal_answer = generate_ideal_answer_only(question, job_role)

    return {
        "score": clean_llm_visuals(score),
        "feedback": clean_llm_visuals(feedback),
        "missing_points": clean_llm_visuals(missing_points),
        "ideal_answer": clean_llm_visuals(ideal_answer)
    }