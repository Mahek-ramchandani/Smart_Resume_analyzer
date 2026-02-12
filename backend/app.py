from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
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
        suggestions.append("Add academic or personal projects.")

    if "internship" not in text:
        suggestions.append("Mention internship or practical experience.")

    if "github" not in text:
        suggestions.append("Add your GitHub profile link.")

    if "sql" not in text and "database" not in text:
        suggestions.append("Add SQL and database related skills.")

    if "communication" not in text:
        suggestions.append("Mention communication and soft skills.")

    return suggestions

def job_match_score(resume_text, job_text):
    if not job_text or job_text.strip() == "":
        return 0
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, job_text])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])
    return round(similarity[0][0] * 100, 2)

CORS(app)

job_roles = {
    "Data Scientist": "python machine learning statistics pandas numpy",
    "Web Developer": "html css javascript react frontend backend",
    "Java Developer": "java spring sql backend",
    "Python Developer": "python flask django api backend"
}

def extract_text(pdf_file):
    text = ""
    reader = PyPDF2.PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text()
    return text.lower()

def analyze_resume(resume_text):
    corpus = [resume_text] + list(job_roles.values())
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(corpus)

    scores = {}
    for i, role in enumerate(job_roles):
        similarity = cosine_similarity(vectors[0], vectors[i+1])[0][0]
        scores[role] = round(similarity * 100, 2)

    return scores

@app.route('/')
def home():
    return "Backend is running successfully!"

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['resume']
    job_desc = request.form.get('job', '')
    resume_text = extract_text(file)

    scores = analyze_resume(resume_text)
    best_role = max(scores, key=scores.get)
    ats = ats_score(resume_text)
    suggestions = generate_suggestions(resume_text)
    jd_match = job_match_score(resume_text, job_desc)

    return jsonify({
        "scores": scores,
        "best_role": best_role,
        "ats_score": ats,
        "suggestions": suggestions,
        "job_match": jd_match
    })

if __name__ == '__main__':
    app.run(debug=True)