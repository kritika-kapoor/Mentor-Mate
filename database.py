import sqlite3

def init_db():
    conn = sqlite3.connect("mentormate.db")
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS resumes (
        resume_id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_file TEXT,
        extracted_text TEXT,
        upload_date DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS job_roles (
        job_role_id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_role_name TEXT,
        created_date DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS interview_questions (
        question_id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_role_id INTEGER,
        question_text TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS evaluation (
        eval_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_answer TEXT,
        score INTEGER,
        feedback TEXT,
        missing_points TEXT,
        ideal_answer TEXT
    )''')
    
    conn.commit()
    conn.close()

def save_resume(filename, text):
    conn = sqlite3.connect("mentormate.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO resumes (resume_file, extracted_text) VALUES (?,?)",
                   (filename, text))
    conn.commit()
    conn.close()

def save_job_role(role):
    conn = sqlite3.connect("mentormate.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO job_roles (job_role_name) VALUES (?)", (role,))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def save_questions(job_role_id, questions):
    conn = sqlite3.connect("mentormate.db")
    cursor = conn.cursor()
    for q in questions:
        cursor.execute("INSERT INTO interview_questions (job_role_id, question_text) VALUES (?,?)",
                       (job_role_id, q))
    conn.commit()
    conn.close()

def save_evaluation(answer, score, feedback, missing, ideal):
    conn = sqlite3.connect("mentormate.db")
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO evaluation 
                      (user_answer, score, feedback, missing_points, ideal_answer)
                      VALUES (?,?,?,?,?)''',
                   (answer, score, feedback, missing, ideal))
    conn.commit()
    conn.close()