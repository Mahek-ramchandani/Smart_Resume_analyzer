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
    resume_text = extract_text(file)

    scores = analyze_resume(resume_text)
    best_role = max(scores, key=scores.get)
    ats = ats_score(resume_text)

    return jsonify({
        "scores": scores,
        "best_role": best_role,
        "ats_score": ats
    })

    def ats_score(resume_text):
        important_keywords = "python java machine learning react sql html css javascript data analysis api cloud"
    resume_words = resume_text.split()
    keywords = important_keywords.split()

    match_count = 0
    for word in keywords:
        if word in resume_words:
            match_count += 1

    score = (match_count / len(keywords)) * 100
    return round(score, 2)

if __name__ == '__main__':
    app.run(debug=True)