import re
from html import escape

def safe_html(text):
    return escape(str(text)).replace("\n", "<br>")

def clean_llm_visuals(text):
    text = str(text)
    text = re.sub(r'```[a-zA-Z]*', '', text)
    text = text.replace("```", "")
    text = re.sub(r'<[^>]*>', '', text)
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    text = re.sub(r'\*\*+', '', text)
    text = re.sub(r'\*+', '', text)
    return text.strip()

def extract_section(raw_text, section_name, next_sections):
    if next_sections:
        pattern = rf"{section_name}\s*:\s*(.*?)(?=\n(?:{'|'.join(next_sections)})\s*:|\Z)"
    else:
        pattern = rf"{section_name}\s*:\s*(.*)"
    match = re.search(pattern, raw_text, re.IGNORECASE | re.DOTALL)
    if match:
        return clean_llm_visuals(match.group(1)).strip()
    return ""

def extract_numeric_score(score_text):
    match = re.search(r"(\d+(\.\d+)?)", str(score_text))
    if match:
        return min(float(match.group(1)), 10.0)
    return 0.0

def get_star_html(score_text):
    score = extract_numeric_score(score_text)
    filled = round(score / 2)
    empty = 5 - filled
    return f"<span class='filled-stars'>{'★' * filled}</span><span class='empty-stars'>{'★' * empty}</span>"

def build_performance_summary(scores):
    if not scores:
        return "No performance summary available."

    avg = sum(scores) / len(scores)

    if avg >= 8.5:
        return "Excellent performance. The candidate showed strong confidence, clarity, and understanding across most questions."
    elif avg >= 7:
        return "Good performance. The candidate answered well overall, with a few areas needing more depth and precision."
    elif avg >= 5:
        return "Average performance. The candidate has basic understanding, but needs stronger structure, confidence, and explanation quality."
    return "Needs improvement. The candidate should practice fundamentals, clarity, and structured answering before the next interview."