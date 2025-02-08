from flask import Flask, request, jsonify, render_template
import os
import sqlite3
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document
import nltk

nltk.download('punkt')

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Predefined Skills & Trends
required_skills = ["python", "java", "machine learning", "data analysis", "sql", "communication","experience","c++","react","c#","ruby","matlab","shell script","scala","perl","golang ","rust"]
industry_trends = ["cloud computing", "ai", "big data", "blockchain","machine learning","cybersecurity","quantum computing","data security","edge computing","data analyst","metaverse","sustainable technology","AR","VR","internet of things"]

# Create Database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS resumes 
                 (id INTEGER PRIMARY KEY, filename TEXT, skills TEXT, score INTEGER, suggestions TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Check Allowed File Type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Extract Text from Resume
def extract_text(file_path):
    text = ""
    if file_path.endswith('.pdf'):
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text()
    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + " "
    return text.lower()

# Extract Skills & Score Resume
def extract_skills(text):
    found_skills = [skill for skill in required_skills if skill in text]
    missing_trends = [trend for trend in industry_trends if trend not in text]
    score = (len(found_skills) / len(required_skills)) * 100
    suggestions = f"Consider learning these trending skills: {', '.join(missing_trends)}"
    return found_skills, score, suggestions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'message': 'No file uploaded'}), 400

    file = request.files['resume']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'message': 'Invalid file type'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    text = extract_text(file_path)
    skills, score, suggestions = extract_skills(text)

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO resumes (filename, skills, score, suggestions) VALUES (?, ?, ?, ?)", 
              (filename, ", ".join(skills), score, suggestions))
    conn.commit()
    conn.close()

    return jsonify({
        'skills_found': skills,
        'score': round(score, 2),
        'suggestions': suggestions
    })

if __name__ == '__main__':
    app.run(debug=True)

