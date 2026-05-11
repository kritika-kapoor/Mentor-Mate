from database import *
init_db()  
import streamlit as st
from resume_utils import load_nlp, extract_resume_text, analyze_resume
from ai_utils import generate_resume_questions, generate_job_role_questions, generate_hr_questions
from evaluation import evaluate_answer, generate_ideal_answer_only
from helpers import safe_html, clean_llm_visuals, extract_numeric_score, build_performance_summary

nlp = load_nlp()


# --- 1. SETTINGS ---
st.set_page_config(page_title="Mentor Mate", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = {}
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'job_role' not in st.session_state:
    st.session_state.job_role = ""
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []
if 'evaluations' not in st.session_state:
    st.session_state.evaluations = []
if 'current_answer' not in st.session_state:
    st.session_state.current_answer = ""
if 'questions_generated' not in st.session_state:
    st.session_state.questions_generated = False
if 'final_evaluation_done' not in st.session_state:
    st.session_state.final_evaluation_done = False
if 'difficulty' not in st.session_state:
    st.session_state.difficulty = "Easy"

if 'current_round' not in st.session_state:
    st.session_state.current_round = "resume"

if 'resume_questions' not in st.session_state:
    st.session_state.resume_questions = []
if 'job_role_questions' not in st.session_state:
    st.session_state.job_role_questions = []
if 'hr_questions' not in st.session_state:
    st.session_state.hr_questions = []

if 'resume_answers' not in st.session_state:
    st.session_state.resume_answers = []
if 'job_role_answers' not in st.session_state:
    st.session_state.job_role_answers = []
if 'hr_answers' not in st.session_state:
    st.session_state.hr_answers = []

if 'resume_done' not in st.session_state:
    st.session_state.resume_done = False
if 'job_role_done' not in st.session_state:
    st.session_state.job_role_done = False
if 'hr_done' not in st.session_state:
    st.session_state.hr_done = False

# --- 2. THEME ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');

.stApp {
    background: #080d1a;
    font-family: 'Inter', sans-serif;
    color: #f1f5f9;
}

.hero-title {
    background: linear-gradient(90deg, #10b981, #3b82f6, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 110px;
    font-weight: 800;
    text-align: center;
    letter-spacing: -5px;
    margin-top: 60px;
    margin-bottom: 0px;
    line-height: 1.1;
}

.feature-bar {
    text-align: center;
    margin-bottom: 8px;
    font-size: 1.3rem;
    font-weight: 400;
    color: #cbd5e1;
    letter-spacing: 1px;
}

.dot {
    color: #3b82f6;
    margin: 0 15px;
    font-weight: 800;
}

.stButton>button {
    background: linear-gradient(90deg, #10b981, #3b82f6);
    color: white !important;
    border: none !important;
    padding: 14px 36px !important;
    border-radius: 50px !important;
    font-weight: 800 !important;
    font-size: 16px !important;
    box-shadow: 0 10px 30px rgba(16, 185, 129, 0.4);
    white-space: nowrap !important;
}

.nav-link,
.nav-link:link,
.nav-link:visited,
.nav-link:active,
.nav-link:focus {
    position: fixed;
    top: 8px;
    left: 28px;
    font-size: 13px;
    color: #e2e8f0;
    text-decoration: none !important;
    font-weight: 700;
    letter-spacing: 0.6px;
    z-index: 999;
    background: linear-gradient(90deg, rgba(16,185,129,0.18), rgba(59,130,246,0.18));
    border: 1px solid rgba(255,255,255,0.10);
    padding: 8px 20px;
    border-radius: 50px !important;
    backdrop-filter: blur(6px);
    transition: background 0.2s, box-shadow 0.2s;
    box-shadow: 0 2px 12px rgba(16,185,129,0.10);
    outline: none !important;
}

.nav-link:hover {
    background: linear-gradient(90deg, rgba(16,185,129,0.30), rgba(59,130,246,0.30));
    box-shadow: 0 4px 20px rgba(59,130,246,0.18);
    color: #fff;
    text-decoration: none !important;
    border-radius: 50px !important;
}

.stSelectbox > div > div {
    cursor: pointer !important;
}
            
.stTextInput>div>div>input, .stTextArea textarea {
    background-color: rgba(255, 255, 255, 0.05) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
}

.stFileUploader section {
    background-color: rgba(255, 255, 255, 0.03) !important;
    border: 1px dashed rgba(255, 255, 255, 0.2) !important;
    border-radius: 12px !important;
}

.card {
    background: rgba(255,255,255,0.05);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 20px;
}

.question-card {
    background: rgba(255,255,255,0.05);
    padding: 14px 22px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 8px;
    margin-top: 4px;
}

.summary-card {
    background: linear-gradient(90deg, rgba(16,185,129,0.15), rgba(59,130,246,0.15));
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 20px;
}

.metric-card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    text-align: center;
    margin-bottom: 15px;
}

.small-head {
    color: #93c5fd;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 10px;
}

.result-box {
    background: rgba(255,255,255,0.05);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 20px;
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 18px;
    flex-wrap: wrap;
    margin-bottom: 12px;
}

.score-pill {
    background: rgba(255,255,255,0.08);
    padding: 8px 16px;
    border-radius: 999px;
    font-size: 14px;
    font-weight: 700;
    color: white;
    border: 1px solid rgba(255,255,255,0.1);
    display: inline-block;
}

.stars {
    font-size: 24px;
    margin-top: 10px;
}

.filled-stars {
    color: #fbbf24;
    letter-spacing: 2px;
}

.empty-stars {
    color: rgba(255,255,255,0.2);
    letter-spacing: 2px;
}

.answer-block {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 12px 14px;
    border-radius: 12px;
    margin-top: 8px;
    margin-bottom: 14px;
    color: white;
    line-height: 1.6;
    white-space: normal;
    word-wrap: break-word;
}

header, footer {
    visibility: hidden;
    height: 0px !important;
    min-height: 0px !important;
}

/* Remove bottom toolbar/footer space Streamlit injects */
.stAppDeployButton, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"],
footer, .reportview-container .main footer {
    display: none !important;
    height: 0 !important;
}

/* Kill ALL bottom dead space */
.main .block-container {
    padding-bottom: 0px !important;
    margin-bottom: 0px !important;
}
section[data-testid="stMain"], [data-testid="stAppViewContainer"] {
    padding-bottom: 0px !important;
    margin-bottom: 0px !important;
}

/* Nuclear bottom space fix */
[data-testid="stBottom"] {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    visibility: hidden !important;
}
.stChatFloatingInputContainer {
    display: none !important;
}
div[class*="StatusWidget"] {
    display: none !important;
}
iframe[title="streamlit_analytics"] {
    display: none !important;
}
.stApp > div {
    overflow: hidden !important;
}

[data-testid="column"] {
    display: flex !important;
    justify-content: center !important;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
""", unsafe_allow_html=True)

# --- LOADING SCREEN ---
def show_loading_screen(message="Generating Questions"):
    import time
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] > section,
    [data-testid="stSidebar"],
    [data-testid="stHeader"],
    footer,
    header {{
        display: none !important;
    }}
    [data-testid="stAppViewContainer"]::before {{
        content: '';
        position: fixed;
        inset: 0;
        background: #0f172a;
        z-index: 9998;
    }}
    #loader-fullscreen {{
        position: fixed;
        inset: 0;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-family: 'Inter', sans-serif;
        pointer-events: none;
    }}
    .ld-spinner {{
        width: 80px; height: 80px;
        border-radius: 50%;
        border: 4px solid rgba(255,255,255,0.06);
        border-top: 4px solid #10b981;
        border-right: 4px solid #3b82f6;
        animation: ldspin 0.9s linear infinite;
        margin-bottom: 32px;
    }}
    @keyframes ldspin {{
        0%   {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    .ld-title {{
        background: linear-gradient(90deg, #10b981, #3b82f6, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 34px; font-weight: 800;
        letter-spacing: -1px; text-align: center;
        margin-bottom: 12px;
    }}
    .ld-sub {{
        color: #475569; font-size: 14px;
        font-weight: 500; text-align: center;
    }}
    </style>
    <div id="loader-fullscreen">
        <svg style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9998;" xmlns="http://www.w3.org/2000/svg">
          <g transform="translate(80,80) rotate(-20)" opacity="0.13">
            <rect x="0" y="0" width="12" height="50" rx="2" fill="#10b981"/>
            <polygon points="0,50 12,50 6,64" fill="#f59e0b"/>
            <rect x="0" y="0" width="12" height="8" rx="2" fill="#94a3b8"/>
          </g>
          <g transform="translate(1300,100)" opacity="0.12">
            <polygon points="20,0 25,14 40,14 28,23 33,37 20,28 7,37 12,23 0,14 15,14" fill="#a78bfa"/>
          </g>
          <circle cx="120" cy="600" r="40" fill="none" stroke="#3b82f6" stroke-width="3" opacity="0.1"/>
          <circle cx="120" cy="600" r="25" fill="none" stroke="#3b82f6" stroke-width="2" opacity="0.08"/>
          <polyline points="1200,620 1220,600 1240,620 1260,600 1280,620 1300,600" fill="none" stroke="#10b981" stroke-width="3" opacity="0.12"/>
          <circle cx="300" cy="150" r="5" fill="#3b82f6" opacity="0.12"/>
          <circle cx="1100" cy="500" r="5" fill="#10b981" opacity="0.12"/>
          <circle cx="200" cy="450" r="4" fill="#a78bfa" opacity="0.10"/>
          <circle cx="1200" cy="200" r="4" fill="#f59e0b" opacity="0.10"/>
          <path d="M60,300 Q40,320 40,340 Q40,360 60,380" fill="none" stroke="#10b981" stroke-width="3" opacity="0.13"/>
          <path d="M1380,300 Q1400,320 1400,340 Q1400,360 1380,380" fill="none" stroke="#10b981" stroke-width="3" opacity="0.13"/>
          <rect x="350" y="550" width="18" height="18" rx="3" fill="none" stroke="#a78bfa" stroke-width="2" opacity="0.10" transform="rotate(15,359,559)"/>
          <rect x="1050" y="120" width="18" height="18" rx="3" fill="none" stroke="#3b82f6" stroke-width="2" opacity="0.10" transform="rotate(-10,1059,129)"/>
        </svg>
        <div class="ld-spinner"></div>
        <div class="ld-title">{message}</div>
        <div class="ld-sub">Please wait a moment...</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(3)


# --- ROUND PROGRESS BAR FUNCTION ---
def show_round_progress(current_round):
    rounds = [
        {"num": 1, "label": "Resume Round", "color": "#3b82f6"},
        {"num": 2, "label": "Job Role Round", "color": "#a78bfa"},
        {"num": 3, "label": "HR Round", "color": "#10b981"},
    ]
    html = '<div style="display:flex; justify-content:center; align-items:center; gap:0px; margin:12px 0 12px 0;">'
    for i, r in enumerate(rounds):
        is_done = r["num"] < current_round
        is_active = r["num"] == current_round
        if is_done:
            circle_bg = r["color"]; circle_border = r["color"]
            label_color = r["color"]; icon = "✓"; font_color = "white"
        elif is_active:
            circle_bg = r["color"]; circle_border = r["color"]
            label_color = "white"; icon = str(r["num"]); font_color = "white"
        else:
            circle_bg = "rgba(255,255,255,0.05)"; circle_border = "rgba(255,255,255,0.15)"
            label_color = "#475569"; icon = str(r["num"]); font_color = "#475569"
        html += f'''
        <div style="display:flex; flex-direction:column; align-items:center; min-width:120px;">
            <div style="width:44px; height:44px; border-radius:50%;
                        background:{circle_bg}; border:2px solid {circle_border};
                        display:flex; align-items:center; justify-content:center;
                        font-size:16px; font-weight:800; color:{font_color};
                        box-shadow: {"0 0 16px " + r["color"] + "88" if is_active else "none"};">
                {icon}
            </div>
            <div style="font-size:11px; font-weight:700; color:{label_color};
                        margin-top:7px; letter-spacing:0.5px; text-align:center;">
                {r["label"]}
            </div>
        </div>
        '''
        if i < len(rounds) - 1:
            line_color = rounds[i]["color"] if current_round > r["num"] else "rgba(255,255,255,0.1)"
            html += f'<div style="width:80px; height:2px; background:{line_color}; margin-bottom:20px;"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# --- ROUND PAGE CSS ---
ROUND_PAGE_CSS = """<style>
html, body, .stApp {
    overflow: hidden !important;
    height: 100vh !important;
}
footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stBottom"] {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    visibility: hidden !important;
}


/* Center buttons within columns */
[data-testid="column"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}
[data-testid="column"] > div {
    width: 100% !important;
}


/* Remove ALL padding from main container */
.main .block-container,
div[data-testid="stMainBlockContainer"],
div[data-testid="block-container"],
.block-container {
    padding-top: 0px !important;
    margin-top: 0px !important;
    padding-bottom: 0px !important;
    margin-bottom: 0px !important;
    padding-left: 5rem !important;
    padding-right: 5rem !important;
}
section[data-testid="stMain"] {
    padding-bottom: 0px !important;
    margin-bottom: 0px !important;
    overflow: hidden !important;
    height: 100vh !important;
}
[data-testid="stAppViewContainer"] {
    height: 100vh !important;
    overflow: hidden !important;
}
/* Textarea - good height, no resize */
.stTextArea textarea {
    height: 160px !important;
    min-height: 160px !important;
    resize: none !important;
}
/* Progress bar pinned, no extra space */
div[data-testid="stProgress"] {
    margin-top: 8px !important;
    margin-bottom: 0px !important;
    padding-bottom: 0px !important;
}
/* Tighten vertical gaps between all elements */
div[data-testid="stVerticalBlock"] > div {
    gap: 0px !important;
}
.stMarkdown { margin-bottom: 0px !important; }
</style>"""


# --- 3. PAGE LOGIC ---
query_params = st.query_params
if "nav" in query_params:
    st.session_state.page = query_params["nav"]
    st.query_params.clear()
    st.rerun()

# ================= PAGE 1 : HOME =================
if st.session_state.page == 'home':

    st.markdown("""
    <svg style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;" viewBox="0 0 1440 900" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
        <radialGradient id="blueGlow" cx="88%" cy="8%" r="40%">
            <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.20"/>
            <stop offset="100%" stop-color="#3b82f6" stop-opacity="0"/>
        </radialGradient>
        <rect width="100%" height="100%" fill="url(#blueGlow)"/>
        <radialGradient id="greenGlow" cx="8%" cy="92%" r="38%">
            <stop offset="0%" stop-color="#10b981" stop-opacity="0.16"/>
            <stop offset="100%" stop-color="#10b981" stop-opacity="0"/>
        </radialGradient>
        <rect width="100%" height="100%" fill="url(#greenGlow)"/>
        <radialGradient id="purpleGlow" cx="50%" cy="50%" r="30%">
            <stop offset="0%" stop-color="#a78bfa" stop-opacity="0.05"/>
            <stop offset="100%" stop-color="#a78bfa" stop-opacity="0"/>
        </radialGradient>
        <rect width="100%" height="100%" fill="url(#purpleGlow)"/>
        <path d="M55,55 L55,28 L82,28" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" opacity="0.22"/>
        <path d="M1385,55 L1385,28 L1358,28" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" opacity="0.22"/>
        <path d="M55,845 L55,872 L82,872" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" opacity="0.22"/>
        <path d="M1385,845 L1385,872 L1358,872" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" opacity="0.22"/>
        <circle cx="130" cy="190" r="3" fill="#10b981" opacity="0.22"/>
        <circle cx="185" cy="140" r="2" fill="#3b82f6" opacity="0.20"/>
        <circle cx="95" cy="310" r="2" fill="#a78bfa" opacity="0.18"/>
        <circle cx="1310" cy="170" r="3" fill="#3b82f6" opacity="0.22"/>
        <circle cx="1375" cy="290" r="2" fill="#10b981" opacity="0.20"/>
        <circle cx="195" cy="730" r="3" fill="#10b981" opacity="0.18"/>
        <circle cx="1305" cy="755" r="3" fill="#3b82f6" opacity="0.18"/>
        <g transform="translate(195,95)" opacity="0.14"><polygon points="10,0 12,7 20,7 14,11 16,18 10,14 4,18 6,11 0,7 8,7" fill="#a78bfa"/></g>
        <g transform="translate(1225,775)" opacity="0.14"><polygon points="10,0 12,7 20,7 14,11 16,18 10,14 4,18 6,11 0,7 8,7" fill="#3b82f6"/></g>
        <g transform="translate(1328,55) rotate(28)" opacity="0.14">
            <rect x="0" y="0" width="7" height="32" rx="2" fill="#10b981"/>
            <polygon points="0,32 7,32 3.5,41" fill="#f59e0b"/>
            <rect x="0" y="0" width="7" height="5" rx="1" fill="#94a3b8"/>
        </g>
        <g transform="translate(95,795) rotate(-22)" opacity="0.14">
            <rect x="0" y="0" width="7" height="32" rx="2" fill="#3b82f6"/>
            <polygon points="0,32 7,32 3.5,41" fill="#f59e0b"/>
            <rect x="0" y="0" width="7" height="5" rx="1" fill="#94a3b8"/>
        </g>
        <circle cx="72" cy="450" r="25" fill="none" stroke="#10b981" stroke-width="1.2" opacity="0.10" stroke-dasharray="3,4"/>
        <circle cx="1368" cy="450" r="25" fill="none" stroke="#3b82f6" stroke-width="1.2" opacity="0.10" stroke-dasharray="3,4"/>
        <polyline points="275,42 290,28 305,42 320,28 335,42" fill="none" stroke="#a78bfa" stroke-width="1.5" stroke-linecap="round" opacity="0.16"/>
        <polyline points="1105,858 1120,843 1135,858 1150,843 1165,858" fill="none" stroke="#10b981" stroke-width="1.5" stroke-linecap="round" opacity="0.16"/>
        <rect x="318" y="782" width="13" height="13" rx="2" fill="none" stroke="#3b82f6" stroke-width="1.2" opacity="0.16" transform="rotate(18,324,788)"/>
        <rect x="1108" y="76" width="13" height="13" rx="2" fill="none" stroke="#10b981" stroke-width="1.2" opacity="0.16" transform="rotate(-14,1114,82)"/>
    </svg>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hero-title">Mentor Mate</div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-bar">AI Interviewer <span class="dot">•</span> Smart Feedback <span class="dot">•</span> Career Analytics</div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    div[data-testid="stButton"] button {
        display: block !important;
        margin: 0 auto !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 0.6, 1])
    with col2:
        if st.button("GET INTERVIEW READY", use_container_width=True):
            st.session_state.page = 'setup'
            st.rerun()

# ================= PAGE 2 : CANDIDATE PROFILE =================
elif st.session_state.page == 'setup':
    st.markdown('<a class="nav-link" href="/?nav=home" target="_self">Home</a>', unsafe_allow_html=True)

    st.markdown('<div class="hero-title" style="font-size:65px; margin-top:30px; margin-bottom:0px;">Candidate Profile</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)

    left, center, right = st.columns([2.5, 4, 2.5])
    with center:
        job_role = st.text_input("JOB ROLE", placeholder="e.g. Software Engineer")
        resume = st.file_uploader("UPLOAD RESUME (PDF)", type=["pdf"])
        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

        if st.button("START INTERVIEW"):
            if job_role and resume:
                st.session_state.resume_text = extract_resume_text(resume)
                st.session_state.resume_data = analyze_resume(st.session_state.resume_text, nlp)
                st.session_state.job_role = job_role
                save_resume(resume.name, st.session_state.resume_text)
                role_id = save_job_role(job_role)
                st.session_state.role_id = role_id
                print("==============================")
                print("SKILLS FOUND:", st.session_state.resume_data.get("skills"))
                print("PROJECTS FOUND:", st.session_state.resume_data.get("projects"))
                print("==============================")

                st.session_state.questions = []
                st.session_state.current_question_index = 0
                st.session_state.user_answers = []
                st.session_state.evaluations = []
                st.session_state.current_answer = ""
                st.session_state.questions_generated = False
                st.session_state.final_evaluation_done = False

                st.session_state.page = "difficulty"
                st.rerun()
            else:
                st.error("Missing information.")


# ================= PAGE 3 : DIFFICULTY SELECTION =================
elif st.session_state.page == 'difficulty':
    st.markdown('<a class="nav-link" href="/?nav=setup" target="_self">Back</a>', unsafe_allow_html=True)

    st.markdown(
        '<div class="hero-title" style="font-size:70px; margin-top:30px; margin-bottom:0px;">Select Interview Level</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="feature-bar">Choose your interview level.</div>',
        unsafe_allow_html=True
    )

    left, center, right = st.columns([2.5, 4, 2.5])

    with center:
        difficulty = st.selectbox(
            "CHOOSE DIFFICULTY LEVEL",
            ["Easy", "Medium", "Hard"],
            index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty)
        )

        st.session_state.difficulty = difficulty

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        if st.button("CONTINUE"):
            st.session_state.current_question_index = 0
            st.session_state.questions = []
            st.session_state.questions_generated = False
            st.session_state.current_answer = ""
            st.session_state.user_answers = []
            st.session_state.resume_answers = []
            st.session_state.job_role_answers = []
            st.session_state.hr_answers = []
            st.session_state.resume_questions = []
            st.session_state.job_role_questions = []
            st.session_state.hr_questions = []
            st.session_state.resume_done = False
            st.session_state.job_role_done = False
            st.session_state.hr_done = False
            st.session_state.evaluations = []
            st.session_state.final_evaluation_done = False
            st.session_state.page = "round_resume"
            st.rerun()


# ================= PAGE 4 : RESUME ROUND =================
elif st.session_state.page == 'round_resume':
    st.markdown(ROUND_PAGE_CSS, unsafe_allow_html=True)

    if not st.session_state.questions_generated:
        show_loading_screen("Generating Questions...")
    else:
        st.markdown('<a class="nav-link" href="/?nav=setup" target="_self">Back</a>', unsafe_allow_html=True)
        show_round_progress(1)
        st.markdown(
            '<div class="hero-title" style="font-size:72px; margin-top:8px; margin-bottom:4px; letter-spacing:-3px;">ROUND ONE</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="feature-bar" style="margin-bottom:12px; margin-top:0px;">Level: {st.session_state.difficulty}</div>',
            unsafe_allow_html=True
        )

    if not st.session_state.questions_generated:
        st.session_state.questions = generate_resume_questions(
            st.session_state.job_role,
            st.session_state.resume_data,
            st.session_state.difficulty
        )
        st.session_state.questions = st.session_state.questions[:15]
        st.session_state.questions_generated = True
        st.rerun()

    if len(st.session_state.questions) == 0:
        st.error("No questions generated.")
    elif len(st.session_state.questions) == 1 and st.session_state.questions[0].startswith("ERROR:"):
        st.error(st.session_state.questions[0])
    else:
        q_index = st.session_state.current_question_index
        total_questions = len(st.session_state.questions)

        if q_index < total_questions:
            current_question = st.session_state.questions[q_index]

            st.markdown(f"""
            <div class="question-card">
                <div class="small-head">Question {q_index + 1} of {total_questions}</div>
                <div style="font-size:24px; font-weight:700; color:white;">{safe_html(current_question)}</div>
            </div>
            """, unsafe_allow_html=True)

            answer = st.text_area(
                "Type your answer",
                value=st.session_state.current_answer,
                height=180,
                key=f"resume_answer_box_{q_index}"
            )

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                submit_label = "SUBMIT ANSWER" if q_index < total_questions - 1 else "FINISH RESUME ROUND"
                if st.button(submit_label, use_container_width=True):
                    if answer.strip():
                        if q_index < len(st.session_state.resume_answers):
                            st.session_state.resume_answers[q_index] = answer.strip()
                        else:
                            st.session_state.resume_answers.append(answer.strip())
                        st.session_state.current_answer = ""
                        st.session_state.current_question_index += 1
                        st.rerun()
                    else:
                        st.warning("Please type your answer first.")

            with col2:
                if st.button("SKIP QUESTION", use_container_width=True):
                    if q_index < len(st.session_state.resume_answers):
                        st.session_state.resume_answers[q_index] = "Skipped"
                    else:
                        st.session_state.resume_answers.append("Skipped")
                    st.session_state.current_answer = ""
                    st.session_state.current_question_index += 1
                    st.rerun()

            with col3:
                if st.button("END ROUND", use_container_width=True):
                    seen = st.session_state.current_question_index
                    if seen == 0:
                        st.session_state.resume_questions = []
                        st.session_state.resume_answers = []
                        st.session_state.resume_done = True
                        st.session_state.current_question_index = 0
                        st.session_state.questions = []
                        st.session_state.questions_generated = False
                        st.session_state.current_answer = ""
                        st.session_state.job_role_answers = []
                        st.session_state.hr_answers = []
                        st.session_state.page = "round_job"
                        st.rerun()
                    else:
                        st.session_state.questions = st.session_state.questions[:seen]
                        st.session_state.resume_answers = st.session_state.resume_answers[:seen]
                        st.session_state.current_question_index = len(st.session_state.questions)
                        st.rerun()

            st.progress(q_index / total_questions)

        else:
            st.session_state.resume_questions = st.session_state.questions
            st.session_state.resume_done = True
            save_questions(st.session_state.role_id, st.session_state.resume_questions)
            st.success("Round One Completed 🎉")

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([6, 1, 1])
            with col3:
                if st.button("NEXT ROUND"):
                    st.session_state.current_question_index = 0
                    st.session_state.questions = []
                    st.session_state.questions_generated = False
                    st.session_state.current_answer = ""
                    st.session_state.job_role_answers = []
                    st.session_state.hr_answers = []
                    st.session_state.page = "round_job"
                    st.rerun()


# ================= PAGE 5 : JOB ROLE ROUND =================
elif st.session_state.page == 'round_job':
    st.markdown(ROUND_PAGE_CSS, unsafe_allow_html=True)

    if not st.session_state.questions_generated:
        show_loading_screen("Generating Questions...")
    else:
        st.markdown('<a class="nav-link" href="/?nav=round_resume" target="_self">Back</a>', unsafe_allow_html=True)
        show_round_progress(2)
        st.markdown(
            '<div class="hero-title" style="font-size:72px; margin-top:8px; margin-bottom:4px; letter-spacing:-3px;">ROUND TWO</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="feature-bar" style="margin-bottom:12px; margin-top:0px;"> {st.session_state.job_role} • Level: {st.session_state.difficulty}</div>',
            unsafe_allow_html=True
        )

    if not st.session_state.questions_generated:
        st.session_state.questions = generate_job_role_questions(
            st.session_state.job_role,
            st.session_state.difficulty
        )
        st.session_state.questions = st.session_state.questions[:15]
        st.session_state.current_question_index = 0
        st.session_state.questions_generated = True
        st.rerun()

    if len(st.session_state.questions) == 0:
        st.error("No questions generated.")
    elif len(st.session_state.questions) == 1 and st.session_state.questions[0].startswith("ERROR:"):
        st.error(st.session_state.questions[0])
    else:
        q_index = st.session_state.current_question_index
        total_questions = len(st.session_state.questions)

        if q_index < total_questions:
            current_question = st.session_state.questions[q_index]

            st.markdown(f"""
            <div class="question-card">
                <div class="small-head">Question {q_index + 1} of {total_questions}</div>
                <div style="font-size:24px; font-weight:700; color:white;">{safe_html(current_question)}</div>
            </div>
            """, unsafe_allow_html=True)

            answer = st.text_area(
                "Type your answer",
                value=st.session_state.current_answer,
                height=180,
                key=f"job_answer_box_{q_index}"
            )

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                submit_label = "SUBMIT ANSWER" if q_index < total_questions - 1 else "FINISH JOB ROLE ROUND"
                if st.button(submit_label, use_container_width=True):
                    if answer.strip():
                        if q_index < len(st.session_state.job_role_answers):
                            st.session_state.job_role_answers[q_index] = answer.strip()
                        else:
                            st.session_state.job_role_answers.append(answer.strip())
                        st.session_state.current_answer = ""
                        st.session_state.current_question_index += 1
                        st.rerun()
                    else:
                        st.warning("Please type your answer first.")

            with col2:
                if st.button("SKIP QUESTION", use_container_width=True):
                    if q_index < len(st.session_state.job_role_answers):
                        st.session_state.job_role_answers[q_index] = "Skipped"
                    else:
                        st.session_state.job_role_answers.append("Skipped")
                    st.session_state.current_answer = ""
                    st.session_state.current_question_index += 1
                    st.rerun()

            with col3:
                if st.button("END ROUND", use_container_width=True):
                    seen = st.session_state.current_question_index
                    if seen == 0:
                        st.session_state.job_role_questions = []
                        st.session_state.job_role_answers = []
                        st.session_state.job_role_done = True
                        st.session_state.current_question_index = 0
                        st.session_state.questions = []
                        st.session_state.questions_generated = False
                        st.session_state.current_answer = ""
                        st.session_state.hr_answers = []
                        st.session_state.page = "round_hr"
                        st.rerun()
                    else:
                        st.session_state.questions = st.session_state.questions[:seen]
                        st.session_state.job_role_answers = st.session_state.job_role_answers[:seen]
                        st.session_state.current_question_index = len(st.session_state.questions)
                        st.rerun()

            st.progress(q_index / total_questions)

        else:
            st.session_state.job_role_questions = st.session_state.questions
            st.session_state.job_role_done = True
            save_questions(st.session_state.role_id, st.session_state.job_role_questions)
            st.success("Round Two Completed 🎉")

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([6, 1, 1])
            with col3:
                if st.button("NEXT ROUND"):
                    st.session_state.current_question_index = 0
                    st.session_state.questions = []
                    st.session_state.questions_generated = False
                    st.session_state.current_answer = ""
                    st.session_state.hr_answers = []
                    st.session_state.page = "round_hr"
                    st.rerun()


# ================= PAGE 6 : HR ROUND =================
elif st.session_state.page == 'round_hr':
    st.markdown(ROUND_PAGE_CSS, unsafe_allow_html=True)

    if not st.session_state.questions_generated:
        show_loading_screen("Generating Questions...")
    else:
        st.markdown('<a class="nav-link" href="/?nav=round_job" target="_self">Back</a>', unsafe_allow_html=True)
        show_round_progress(3)
        st.markdown(
            '<div class="hero-title" style="font-size:72px; margin-top:8px; margin-bottom:4px; letter-spacing:-3px;">ROUND THREE</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="feature-bar" style="margin-bottom:12px; margin-top:0px;"> Level: {st.session_state.difficulty}</div>',
            unsafe_allow_html=True
        )

    if not st.session_state.questions_generated:
        st.session_state.questions = generate_hr_questions(
            st.session_state.job_role,
            st.session_state.difficulty
        )
        st.session_state.questions = st.session_state.questions[:10]
        st.session_state.current_question_index = 0
        st.session_state.hr_answers = []
        st.session_state.questions_generated = True
        st.rerun()

    if len(st.session_state.questions) == 0:
        st.error("No questions generated.")
    elif len(st.session_state.questions) == 1 and st.session_state.questions[0].startswith("ERROR:"):
        st.error(st.session_state.questions[0])
    else:
        q_index = st.session_state.current_question_index
        total_questions = len(st.session_state.questions)

        if q_index < total_questions:
            current_question = st.session_state.questions[q_index]

            st.markdown(f"""
            <div class="question-card">
                <div class="small-head">Question {q_index + 1} of {total_questions}</div>
                <div style="font-size:24px; font-weight:700; color:white;">{safe_html(current_question)}</div>
            </div>
            """, unsafe_allow_html=True)

            answer = st.text_area(
                "Type your answer",
                value=st.session_state.current_answer,
                height=180,
                key=f"hr_answer_box_{q_index}"
            )

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                submit_label = "SUBMIT ANSWER" if q_index < total_questions - 1 else "FINISH HR ROUND"
                if st.button(submit_label, use_container_width=True):
                    if answer.strip():
                        if q_index < len(st.session_state.hr_answers):
                            st.session_state.hr_answers[q_index] = answer.strip()
                        else:
                            st.session_state.hr_answers.append(answer.strip())
                        st.session_state.current_answer = ""
                        st.session_state.current_question_index += 1
                        st.rerun()
                    else:
                        st.warning("Please type your answer first.")

            with col2:
                if st.button("SKIP QUESTION", use_container_width=True):
                    if q_index < len(st.session_state.hr_answers):
                        st.session_state.hr_answers[q_index] = "Skipped"
                    else:
                        st.session_state.hr_answers.append("Skipped")
                    st.session_state.current_answer = ""
                    st.session_state.current_question_index += 1
                    st.rerun()

            with col3:
                if st.button("END ROUND", use_container_width=True):
                    seen = st.session_state.current_question_index
                    if seen == 0:
                        st.session_state.hr_questions = []
                        st.session_state.hr_answers = []
                        st.session_state.hr_done = True
                        st.session_state.page = "analysis_select"
                        st.rerun()
                    else:
                        st.session_state.questions = st.session_state.questions[:seen]
                        st.session_state.hr_answers = st.session_state.hr_answers[:seen]
                        st.session_state.current_question_index = len(st.session_state.questions)
                        st.rerun()

            st.progress(q_index / total_questions)

        else:
            st.session_state.hr_questions = st.session_state.questions
            st.session_state.hr_done = True

            if not st.session_state.final_evaluation_done:
                show_loading_screen("Preparing Your Analysis...")
                all_questions = (
                    st.session_state.resume_questions +
                    st.session_state.job_role_questions +
                    st.session_state.hr_questions
                )
                all_answers = (
                    st.session_state.resume_answers +
                    st.session_state.job_role_answers +
                    st.session_state.hr_answers
                )
                st.session_state.user_answers = all_answers
                st.session_state.evaluations = []
                safe_count = min(len(all_questions), len(all_answers))
                for i in range(safe_count):
                    question = all_questions[i]
                    answer_text = all_answers[i]
                    if answer_text.strip().lower() == "skipped":
                        result = {
                            "score": "0/10",
                            "feedback": "This question was skipped.",
                            "missing_points": "No response was given.",
                            "ideal_answer": generate_ideal_answer_only(question, st.session_state.job_role)
                        }
                    else:
                        result = evaluate_answer(question, answer_text, st.session_state.job_role)
                    st.session_state.evaluations.append(result)
                st.session_state.final_evaluation_done = True
                for eval_result in st.session_state.evaluations:
                    save_evaluation(
                        "",
                        eval_result.get("score", ""),
                        eval_result.get("feedback", ""),
                        eval_result.get("missing_points", ""),
                        eval_result.get("ideal_answer", "")
                    )

            st.session_state.page = "analysis_select"
            st.rerun()


# ================= PAGE 7 : ANALYSIS SELECTION =================
elif st.session_state.page == "analysis_select":
    st.markdown("""<style>
    html, body, .stApp { overflow: hidden !important; height: 100vh !important; }
    footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], [data-testid="stBottom"] {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
    }
    .main .block-container, div[data-testid="stMainBlockContainer"],
    div[data-testid="block-container"], .block-container {
        padding-top: 0px !important; margin-top: 0px !important;
        padding-bottom: 0px !important;
    }

    /* ── Make both action buttons identical gradient style ── */
    div[data-testid="stButton"] button,
    div[data-testid="stDownloadButton"] button {
        background: linear-gradient(90deg, #10b981, #3b82f6) !important;
        color: white !important;
        border: none !important;
        padding: 14px 36px !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.4) !important;
        width: 100% !important;
    }
    </style>""", unsafe_allow_html=True)

    def score_color(s):
        if s >= 8: return "#10b981"
        if s >= 5: return "#f59e0b"
        return "#ef4444"

    def score_label(s):
        if s >= 8: return "Excellent"
        if s >= 5: return "Average"
        return "Needs Work"

    def render_analysis(questions, answers, evaluations, round_title, accent_color):
        if not questions or not evaluations:
            st.error("No data available for this round.")
            return

        safe_total = min(len(questions), len(answers) if answers else len(evaluations), len(evaluations))
        scores_list = [int(round(extract_numeric_score(clean_llm_visuals(evaluations[i]["score"])))) for i in range(safe_total)]
        average_score = int(round(sum(scores_list) / len(scores_list))) if scores_list else 0
        highest_score = int(max(scores_list)) if scores_list else 0
        lowest_score  = int(min(scores_list)) if scores_list else 0
        performance_summary = build_performance_summary(scores_list)
        avg_color = score_color(average_score)

        st.markdown(
            f'<div class="hero-title" style="font-size:65px; margin-top:0px; margin-bottom:0px;">{round_title}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="feature-bar" style="margin-bottom:10px;">{st.session_state.job_role} &nbsp;•&nbsp; {st.session_state.difficulty} Level</div>',
            unsafe_allow_html=True
        )

        st.markdown(f"""
        <div style="background:linear-gradient(135deg, rgba(16,185,129,0.12), rgba(59,130,246,0.10));
                    border:1px solid rgba(255,255,255,0.1); border-radius:24px;
                    padding:32px 40px; margin-bottom:28px; text-align:center;">
            <div style="font-size:13px; color:#94a3b8; letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;">Overall Performance</div>
            <div style="font-size:68px; font-weight:900; color:{avg_color}; line-height:1;">
                {average_score}<span style="font-size:28px; color:#64748b;">/10</span>
            </div>
            <div style="font-size:16px; color:#cbd5e1; margin-top:10px; line-height:1.7;">{performance_summary}</div>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""<div class="metric-card">
                <div style="font-size:12px; color:#94a3b8; letter-spacing:1.5px; text-transform:uppercase;">Total Questions</div>
                <div style="font-size:40px; font-weight:900; color:white; margin:6px 0;">{safe_total}</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class="metric-card">
                <div style="font-size:12px; color:#94a3b8; letter-spacing:1.5px; text-transform:uppercase;">Best Score</div>
                <div style="font-size:40px; font-weight:900; color:#10b981; margin:6px 0;">{highest_score}<span style="font-size:18px; color:#64748b;">/10</span></div>
            </div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""<div class="metric-card">
                <div style="font-size:12px; color:#94a3b8; letter-spacing:1.5px; text-transform:uppercase;">Lowest Score</div>
                <div style="font-size:40px; font-weight:900; color:#ef4444; margin:6px 0;">{lowest_score}<span style="font-size:18px; color:#64748b;">/10</span></div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:20px; font-weight:800; color:#e2e8f0; margin-bottom:16px;">📋 Question Breakdown</div>', unsafe_allow_html=True)

        for i in range(safe_total):
            question      = questions[i]
            answer_text   = answers[i] if answers and i < len(answers) else "Skipped"
            eval_data     = evaluations[i]
            score_text    = clean_llm_visuals(eval_data["score"])
            feedback_text = clean_llm_visuals(eval_data["feedback"])
            missing_text  = clean_llm_visuals(eval_data["missing_points"])
            ideal_text    = clean_llm_visuals(eval_data["ideal_answer"])
            numeric       = int(round(extract_numeric_score(score_text)))
            s_color       = score_color(numeric)
            s_label       = score_label(numeric)

            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
                        border-radius:20px; padding:24px 28px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px; margin-bottom:12px;">
                    <span style="font-size:11px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase;
                                 color:{accent_color}; background:rgba(255,255,255,0.06);
                                 padding:4px 14px; border-radius:999px; border:1px solid {accent_color}55;">
                        {round_title}
                    </span>
                    <div style="text-align:center;">
                        <div style="font-size:32px; font-weight:900; color:{s_color}; line-height:1;">
                            {numeric}<span style="font-size:15px; color:#64748b;">/10</span>
                        </div>
                        <div style="font-size:11px; color:{s_color}; font-weight:700; letter-spacing:1px;">{s_label}</div>
                    </div>
                </div>
                <div style="font-size:17px; font-weight:700; color:white; line-height:1.5; margin-bottom:14px;">
                    Q{i+1}. {question}
                </div>
                <div style="font-size:11px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#94a3b8; margin-bottom:6px;">YOUR ANSWER</div>
                <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
                            border-radius:10px; padding:12px 16px; color:#e2e8f0; font-size:14px; line-height:1.7; margin-bottom:0;">
                    {answer_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

            fc, mc, ic = st.columns(3)
            with fc:
                st.markdown(f"""
                <div style="background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.25);
                            border-radius:14px; padding:16px 18px; margin-bottom:4px;">
                    <div style="font-size:11px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#93c5fd; margin-bottom:8px;">💬 Feedback</div>
                    <div style="color:#dbeafe; font-size:14px; line-height:1.7;">{feedback_text}</div>
                </div>""", unsafe_allow_html=True)
            with mc:
                st.markdown(f"""
                <div style="background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.25);
                            border-radius:14px; padding:16px 18px; margin-bottom:4px;">
                    <div style="font-size:11px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#fcd34d; margin-bottom:8px;">⚠️ Missing Points</div>
                    <div style="color:#fef3c7; font-size:14px; line-height:1.7;">{missing_text}</div>
                </div>""", unsafe_allow_html=True)
            with ic:
                st.markdown(f"""
                <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25);
                            border-radius:14px; padding:16px 18px; margin-bottom:4px;">
                    <div style="font-size:11px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#6ee7b7; margin-bottom:8px;">✅ Ideal Answer</div>
                    <div style="color:#d1fae5; font-size:14px; line-height:1.7;">{ideal_text}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Compute per-round evaluations once ──────────────────────────────
    if not st.session_state.final_evaluation_done:
        show_loading_screen("Preparing Your Analysis...")
        all_questions = (
            st.session_state.resume_questions +
            st.session_state.job_role_questions +
            st.session_state.hr_questions
        )
        all_answers = (
            st.session_state.resume_answers +
            st.session_state.job_role_answers +
            st.session_state.hr_answers
        )
        st.session_state.evaluations = []
        safe_count = min(len(all_questions), len(all_answers))
        for i in range(safe_count):
            q = all_questions[i]
            a = all_answers[i]
            if a.strip().lower() == "skipped":
                result = {
                    "score": "0/10",
                    "feedback": "This question was skipped.",
                    "missing_points": "No response was given.",
                    "ideal_answer": generate_ideal_answer_only(q, st.session_state.job_role)
                }
            else:
                result = evaluate_answer(q, a, st.session_state.job_role)
            st.session_state.evaluations.append(result)
        st.session_state.final_evaluation_done = True
        st.rerun()

    # Split evaluations into per-round lists
    r1_len = len(st.session_state.resume_questions)
    r2_len = len(st.session_state.job_role_questions)
    r3_len = len(st.session_state.hr_questions)
    all_evals = st.session_state.evaluations
    r1_evals = all_evals[:r1_len]
    r2_evals = all_evals[r1_len:r1_len + r2_len]
    r3_evals = all_evals[r1_len + r2_len:]

    if "analysis_page" not in st.session_state:
        st.session_state.analysis_page = "select"

    # ── SELECTION SCREEN ────────────────────────────────────────────────
    if st.session_state.analysis_page == "select":

        st.markdown(
            '<div class="hero-title" style="font-size:75px; margin-top:0px;">Interview Complete!</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="feature-bar" style="margin-bottom:10px;">All 3 rounds done. Which analysis do you want to see?</div>',
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)

        def avg(evals):
            if not evals: return 0
            scores = [extract_numeric_score(clean_llm_visuals(e["score"])) for e in evals]
            return int(round(sum(scores) / len(scores)))

        r1_avg = avg(r1_evals)
        r2_avg = avg(r2_evals)
        r3_avg = avg(r3_evals)

        c1_color = score_color(r1_avg)
        c2_color = score_color(r2_avg)
        c3_color = score_color(r3_avg)
        r1_q = len(st.session_state.resume_questions)
        r2_q = len(st.session_state.job_role_questions)
        r3_q = len(st.session_state.hr_questions)

        with c1:
            st.markdown(
                "<div style='background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);"
                "border-radius:20px;padding:30px 24px;text-align:center;margin-bottom:12px;'>"
                "<div style='font-size:20px;font-weight:800;color:white;margin-bottom:6px;'>Round 1</div>"
                "<div style='font-size:14px;color:#93c5fd;margin-bottom:14px;'>Resume Based</div>"
                "<div style='font-size:32px;font-weight:900;color:" + c1_color + ";'>" + str(r1_avg) +
                "<span style='font-size:16px;color:#64748b;'>/10</span></div>"
                "<div style='font-size:12px;color:#94a3b8;margin-top:4px;'>" + str(r1_q) + " questions</div>"
                "</div>",
                unsafe_allow_html=True
            )
            if st.button("View Round 1 Analysis", use_container_width=True):
                st.session_state.analysis_page = "round1"
                st.rerun()

        with c2:
            st.markdown(
                "<div style='background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.3);"
                "border-radius:20px;padding:30px 24px;text-align:center;margin-bottom:12px;'>"
                "<div style='font-size:20px;font-weight:800;color:white;margin-bottom:6px;'>Round 2</div>"
                "<div style='font-size:14px;color:#c4b5fd;margin-bottom:14px;'>Job Role Based</div>"
                "<div style='font-size:32px;font-weight:900;color:" + c2_color + ";'>" + str(r2_avg) +
                "<span style='font-size:16px;color:#64748b;'>/10</span></div>"
                "<div style='font-size:12px;color:#94a3b8;margin-top:4px;'>" + str(r2_q) + " questions</div>"
                "</div>",
                unsafe_allow_html=True
            )
            if st.button("View Round 2 Analysis", use_container_width=True):
                st.session_state.analysis_page = "round2"
                st.rerun()

        with c3:
            st.markdown(
                "<div style='background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);"
                "border-radius:20px;padding:30px 24px;text-align:center;margin-bottom:12px;'>"
                "<div style='font-size:20px;font-weight:800;color:white;margin-bottom:6px;'>Round 3</div>"
                "<div style='font-size:14px;color:#6ee7b7;margin-bottom:14px;'>HR Round</div>"
                "<div style='font-size:32px;font-weight:900;color:" + c3_color + ";'>" + str(r3_avg) +
                "<span style='font-size:16px;color:#64748b;'>/10</span></div>"
                "<div style='font-size:12px;color:#94a3b8;margin-top:4px;'>" + str(r3_q) + " questions</div>"
                "</div>",
                unsafe_allow_html=True
            )
            if st.button("View Round 3 Analysis", use_container_width=True):
                st.session_state.analysis_page = "round3"
                st.rerun()

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.07); margin:8px 0 16px 0;'>", unsafe_allow_html=True)

        # ── PDF DOWNLOAD BUTTON ─────────────────────────────────────────
        def generate_pdf_report():
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
            from reportlab.lib.units import cm
            import io

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                    rightMargin=2*cm, leftMargin=2*cm,
                                    topMargin=2*cm, bottomMargin=2*cm)

            styles = getSampleStyleSheet()
            story = []

            title_style = ParagraphStyle('Title', fontSize=26, fontName='Helvetica-Bold',
                                         textColor=colors.HexColor('#1e293b'), spaceAfter=6, alignment=1)
            sub_style = ParagraphStyle('Sub', fontSize=12, fontName='Helvetica',
                                       textColor=colors.HexColor('#64748b'), spaceAfter=20, alignment=1)
            story.append(Paragraph("Mentor Mate", title_style))
            story.append(Paragraph(f"Interview Analysis Report", sub_style))
            story.append(Paragraph(f"Candidate: {st.session_state.get('candidate_name','Candidate')}  |  Role: {st.session_state.get('job_role','N/A')}  |  Level: {st.session_state.get('difficulty','N/A')}", sub_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
            story.append(Spacer(1, 0.3*cm))

            heading_style = ParagraphStyle('Heading', fontSize=14, fontName='Helvetica-Bold',
                                           textColor=colors.HexColor('#1e293b'), spaceAfter=8, spaceBefore=14)
            story.append(Paragraph("Overall Summary", heading_style))

            all_evals = st.session_state.evaluations
            r1_len = len(st.session_state.resume_questions)
            r2_len = len(st.session_state.job_role_questions)
            r1e = all_evals[:r1_len]
            r2e = all_evals[r1_len:r1_len+r2_len]
            r3e = all_evals[r1_len+r2_len:]

            def avg_score(evals):
                if not evals: return 0
                sc = [extract_numeric_score(clean_llm_visuals(e["score"])) for e in evals]
                return int(round(sum(sc)/len(sc)))

            summary_data = [
                ["Round", "Questions", "Avg Score"],
                ["Round 1 – Resume", str(len(st.session_state.resume_questions)), f"{avg_score(r1e)}/10"],
                ["Round 2 – Job Role", str(len(st.session_state.job_role_questions)), f"{avg_score(r2e)}/10"],
                ["Round 3 – HR", str(len(st.session_state.hr_questions)), f"{avg_score(r3e)}/10"],
            ]
            t = Table(summary_data, colWidths=[8*cm, 4*cm, 4*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
                ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
                ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE',   (0,0), (-1,-1), 11),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.white]),
                ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('ALIGN',      (1,0), (-1,-1), 'CENTER'),
                ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.4*cm))

            q_style  = ParagraphStyle('Q', fontSize=11, fontName='Helvetica-Bold',
                                      textColor=colors.HexColor('#1e293b'), spaceAfter=4, spaceBefore=10)
            ans_style = ParagraphStyle('A', fontSize=10, fontName='Helvetica',
                                       textColor=colors.HexColor('#475569'), spaceAfter=3)
            label_style = ParagraphStyle('L', fontSize=9, fontName='Helvetica-Bold',
                                         textColor=colors.HexColor('#64748b'), spaceAfter=2)
            body_style  = ParagraphStyle('B', fontSize=10, fontName='Helvetica',
                                         textColor=colors.HexColor('#334155'), spaceAfter=4)

            rounds_data = [
                ("Round 1 – Resume", st.session_state.resume_questions, st.session_state.resume_answers, r1e, '#3b82f6'),
                ("Round 2 – Job Role", st.session_state.job_role_questions, st.session_state.job_role_answers, r2e, '#7c3aed'),
                ("Round 3 – HR", st.session_state.hr_questions, st.session_state.hr_answers, r3e, '#059669'),
            ]

            for round_title, questions, answers, evals, color_hex in rounds_data:
                if not questions or not evals: continue
                story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
                story.append(Paragraph(round_title, heading_style))
                safe = min(len(questions), len(evals))
                for i in range(safe):
                    q = questions[i]
                    a = answers[i] if answers and i < len(answers) else "Skipped"
                    ev = evals[i]
                    score_val = int(round(extract_numeric_score(clean_llm_visuals(ev["score"]))))
                    story.append(Paragraph(f"Q{i+1}. {q}", q_style))
                    story.append(Paragraph(f"Your Answer: {a}", ans_style))
                    story.append(Paragraph(f"Score: {score_val}/10", label_style))
                    story.append(Paragraph(f"Feedback: {clean_llm_visuals(ev.get('feedback',''))}", body_style))
                    story.append(Paragraph(f"Missing Points: {clean_llm_visuals(ev.get('missing_points',''))}", body_style))
                    story.append(Paragraph(f"Ideal Answer: {clean_llm_visuals(ev.get('ideal_answer',''))}", body_style))

            doc.build(story)
            buffer.seek(0)
            return buffer.read()
        _, _, btn_col1, btn_col2 = st.columns([4, 1, 1, 1])

        with btn_col1:
            if st.button("Start Over", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        with btn_col2:
            try:
                pdf_bytes = generate_pdf_report()
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=f"mentormate_analysis_{st.session_state.get('job_role','report').replace(' ','_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF generation failed: {e}. Run: pip install reportlab")

    # ── ROUND 1 ANALYSIS ────────────────────────────────────────────────
    elif st.session_state.analysis_page == "round1":
        if st.button("← Back to Selection"):
            st.session_state.analysis_page = "select"
            st.rerun()
        render_analysis(
            st.session_state.resume_questions,
            st.session_state.resume_answers,
            r1_evals,
            "Round 1 · Resume",
            "#3b82f6"
        )

    # ── ROUND 2 ANALYSIS ────────────────────────────────────────────────
    elif st.session_state.analysis_page == "round2":
        if st.button("← Back to Selection"):
            st.session_state.analysis_page = "select"
            st.rerun()
        render_analysis(
            st.session_state.job_role_questions,
            st.session_state.job_role_answers,
            r2_evals,
            "Round 2 · Job Role",
            "#a78bfa"
        )

    # ── ROUND 3 ANALYSIS ────────────────────────────────────────────────
    elif st.session_state.analysis_page == "round3":
        if st.button("← Back to Selection"):
            st.session_state.analysis_page = "select"
            st.rerun()
        render_analysis(
            st.session_state.hr_questions,
            st.session_state.hr_answers,
            r3_evals,
            "Round 3 · HR",
            "#10b981"
        )


