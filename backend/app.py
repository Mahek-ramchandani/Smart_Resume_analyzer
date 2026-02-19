from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import sqlite3
import os
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Simple Flask app initialization
app = Flask(__name__)
CORS(app)
app.secret_key = "resume_secret_key_123"

# ============== DATABASE ==============

def get_db():
    return sqlite3.connect("database.db")

def create_tables():
    con = get_db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            score REAL,
            job_desc TEXT
        )
    """)

    con.commit()
    con.close()

create_tables()

# ============== ANALYSIS FUNCTIONS ==============

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text()
    except:
        text = "Error reading PDF"
    return text.lower()

def ats_score(text):
    keywords = [
        "python", "java", "sql", "machine learning", "react", "flask",
        "api", "html", "css", "javascript", "git", "github", "project",
        "internship", "database", "cloud", "aws", "azure"
    ]

    text = text.lower()
    match_count = sum(1 for word in keywords if word in text)
    score = (match_count / len(keywords)) * 100
    return round(score, 2)

def generate_suggestions(text):
    suggestions = []
    text = text.lower()
    
    if "project" not in text:
        suggestions.append("✅ Add academic or personal projects.")
    if "internship" not in text:
        suggestions.append("✅ Mention internship or practical experience.")
    if "github" not in text:
        suggestions.append("✅ Add your GitHub profile link.")
    if "sql" not in text and "database" not in text:
        suggestions.append("✅ Add SQL and database related skills.")
    if "communication" not in text and "teamwork" not in text:
        suggestions.append("✅ Mention communication and soft skills.")
    
    return suggestions[:3]

def job_match_score(resume_text, job_text=""):
    if not job_text or job_text.strip() == "":
        job_text = "python developer machine learning data science flask api backend frontend react javascript"
    
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, job_text])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])
    return round(similarity[0][0] * 100, 2)

# ============== ROUTES ==============

@app.route('/test')
def test():
    return "✅ Flask is working!", 200

@app.route('/')
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        return f"Template Error: {str(e)}", 500

# ===== WITHOUT LOGIN ANALYZE =====
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['resume']
    job_desc = request.form.get('job_desc', '')
    
    resume_text = extract_text_from_pdf(file)
    
    score = job_match_score(resume_text, job_desc)
    ats = ats_score(resume_text)
    suggestions = generate_suggestions(resume_text)
    
    return jsonify({
        "ATS_Score": ats,
        "Job_Match": score,
        "suggestions": suggestions,
        "message": "Resume analyzed successfully!"
    })

# ===== SIGNUP =====
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        con = get_db()
        cur = con.cursor()
        
        # Check if email already exists
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        if cur.fetchone():
            con.close()
            return "Email already exists!", 400
        
        cur.execute("INSERT INTO users VALUES(NULL,?,?,?)", (name, email, password))
        con.commit()
        con.close()
        
        return redirect(url_for('login'))
    
    return render_template("signup.html")

# ===== LOGIN =====
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cur.fetchone()
        con.close()
        
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            return "Invalid Login! Email or Password incorrect.", 400
    
    return render_template("login.html")

# ===== DASHBOARD =====
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT score FROM history WHERE user_id=?", (session['user_id'],))
    scores = cur.fetchall()
    con.close()
    
    avg_score = round(sum([s[0] for s in scores]) / len(scores), 2) if scores else 0
    
    return render_template("dashboard.html", 
                         scores=scores, 
                         avg_score=avg_score,
                         user_name=session.get('user_name'))

# ===== DASHBOARD ANALYZE (WITH LOGIN) =====
@app.route('/dashboard-analyze', methods=['POST'])
def dashboard_analyze():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['resume']
    job_desc = request.form.get('job_desc', '')
    
    resume_text = extract_text_from_pdf(file)
    score = job_match_score(resume_text, job_desc)
    ats = ats_score(resume_text)
    suggestions = generate_suggestions(resume_text)
    
    # Save to history
    con = get_db()
    cur = con.cursor()
    cur.execute("INSERT INTO history VALUES(NULL,?,?,?)", 
                (session['user_id'], score, job_desc))
    con.commit()
    con.close()
    
    return jsonify({
        "ATS_Score": ats,
        "Job_Match": score,
        "suggestions": suggestions
    })

# ===== LOGOUT =====
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ===== CHATBOT =====
@app.route('/chat', methods=['POST'])
def chatbot():
    data = request.get_json()
    msg = data.get('message', '').lower()
    
    if "resume" in msg or "cv" in msg:
        reply = "📝 Make sure your resume has: Skills, Projects, Keywords, and Experience. Keep it to 1 page!"
    elif "interview" in msg:
        reply = "🎤 Practice HR + Technical questions daily. Do mock interviews. Show confidence!"
    elif "ats" in msg or "score" in msg:
        reply = "🚀 ATS Score checks for keywords. Use technical terms, metrics, and action verbs!"
    elif "skill" in msg or "skills" in msg:
        reply = "💡 Add relevant skills. Use industry keywords like Python, React, SQL, AWS, etc."
    elif "project" in msg:
        reply = "🎯 Add 2-3 strong projects with GitHub links. Show what you built and learned!"
    elif "experience" in msg or "job" in msg:
        reply = "💼 Highlight your achievements. Use numbers: 'Increased sales by 30%' instead of just duties."
    else:
        reply = "💬 Ask me about: Resume, Interview, ATS, Skills, Projects, or Experience. I'm here to help!"
    
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)