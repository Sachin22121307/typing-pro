from flask import Flask, render_template, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FILE = 'data.db'

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS passages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE,
                body TEXT
            )
        """)
        db.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/passages', methods=['GET'])
def get_passages():
    db = get_db()
    passages = db.execute("SELECT id, title, body FROM passages").fetchall()
    return jsonify([dict(p) for p in passages])

@app.route('/api/passages', methods=['POST'])
def add_passage():
    data = request.json
    title = data.get('title', '').strip()
    body = data.get('body', '').strip()
    if not title or not body:
        return jsonify({'error': 'Title and body required'}), 400
    try:
        db = get_db()
        db.execute("INSERT INTO passages (title, body) VALUES (?, ?)", (title, body))
        db.commit()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Passage title must be unique'}), 400

@app.route('/api/passages/<int:pid>', methods=['PUT'])
def edit_passage(pid):
    data = request.json
    title = data.get('title', '').strip()
    body = data.get('body', '').strip()
    if not title or not body:
        return jsonify({'error': 'Title and body required'}), 400
    db = get_db()
    db.execute("UPDATE passages SET title=?, body=? WHERE id=?", (title, body, pid))
    db.commit()
    return jsonify({'success': True})

@app.route('/api/passages/<int:pid>', methods=['DELETE'])
def delete_passage(pid):
    db = get_db()
    db.execute("DELETE FROM passages WHERE id=?", (pid,))
    db.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
