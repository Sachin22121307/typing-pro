from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import time
from datetime import datetime
import re
from difflib import SequenceMatcher

app = Flask(__name__)
CORS(app)

# Initialize DB (simple example)
def init_db():
    conn = sqlite3.connect('data.db')
    conn.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            typed_text TEXT,
            wpm REAL,
            accuracy REAL,
            errors INTEGER,
            timestamp TEXT
        )""")
    conn.commit()
    conn.close()

def analyze_typing(original_text, typed_text, duration):
    # Simplified logic as example
    original_words = re.findall(r"\\b\\w+\\b", original_text.lower())
    typed_words = re.findall(r"\\b\\w+\\b", typed_text.lower())

    matcher = SequenceMatcher(None, original_words, typed_words)
    errors = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            errors += max(i2 - i1, j2 - j1)
    total_words = len(original_words)
    accuracy = max(0, 100 - round(errors * 100 / total_words if total_words > 0 else 0, 2))
    wpm = len(typed_words) * 60 / duration if duration > 0 else 0
    return wpm, accuracy, errors

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/check', methods=['POST'])
def check():
    data = request.json
    original = data.get('original')
    typed = data.get('typed')
    duration = data.get('duration')  # seconds

    wpm, accuracy, errors = analyze_typing(original, typed, duration)

    conn = sqlite3.connect('data.db')
    conn.execute("""
        INSERT INTO results (typed_text, wpm, accuracy, errors, timestamp)
        VALUES (?, ?, ?, ?, ?)""",
                 (typed, wpm, accuracy, errors, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return jsonify({
        'wpm': wpm,
        'accuracy': accuracy,
        'errors': errors
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
