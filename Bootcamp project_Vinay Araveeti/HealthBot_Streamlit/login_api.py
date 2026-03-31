"""
Login API using Flask
Verifies user credentials against SQLite database
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from pathlib import Path
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Get database path
DB_PATH = Path(__file__).parent / "users_database.db"

def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def load_users():
    """Load users from SQLite database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT email_username, password, name FROM Login')
        rows = cursor.fetchall()
        conn.close()
        
        users = {}
        for row in rows:
            email = row[0].strip().lower()
            password = row[1].strip()
            name = row[2]
            users[email] = {"password": password, "name": name}
        
        return users
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def save_search_history(email, topic, grade=""):
    """Save search topic to history table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        date = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''
            INSERT INTO Search_History (email_username, search_topic, date, grade)
            VALUES (?, ?, ?, ?)
        ''', (email.lower(), topic, date, grade))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False

def update_search_grade(email, topic, grade):
    """Update grade for a completed search"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE Search_History 
            SET grade = ? 
            WHERE email_username = ? AND search_topic = ? AND grade = ''
        ''', (grade, email.lower(), topic))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating grade: {e}")
        return False

@app.route('/api/login', methods=['POST'])
def login():
    """
    Login endpoint
    Expected JSON: {"email": "user@example.com", "password": "password"}
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Email and password are required"
            }), 400
        
        users = load_users()
        
        if email in users:
            if users[email]['password'] == password:
                return jsonify({
                    "success": True,
                    "message": "Login successful",
                    "user": {
                        "email": email,
                        "name": users[email]['name']
                    }
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "message": "Invalid password"
                }), 401
        else:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@app.route('/api/register', methods=['POST'])
def register():
    """
    Register new user
    Expected JSON: {"email": "user@example.com", "password": "password", "name": "User Name"}
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        name = data.get('name', 'User').strip()
        
        if not email or not password or len(password) < 6:
            return jsonify({
                "success": False,
                "message": "Invalid email or password (min 6 chars)"
            }), 400
        
        users = load_users()
        
        if email in users:
            return jsonify({
                "success": False,
                "message": "User already exists"
            }), 409
        
        # Add to SQLite
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Login (email_username, password, name)
                VALUES (?, ?, ?)
            ''', (email, password, name))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:
            return jsonify({
                "success": False,
                "message": "User already exists"
            }), 409
        
        return jsonify({
            "success": True,
            "message": "Registration successful",
            "user": {
                "email": email,
                "name": name
            }
        }), 201
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@app.route('/api/search-history/<email>', methods=['GET'])
def get_search_history(email):
    """Get search history for a user"""
    try:
        email = email.lower()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT search_topic, date, grade FROM Search_History WHERE email_username = ?', (email,))
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                "topic": row[0],
                "date": row[1],
                "grade": row[2] or "Pending"
            })
        
        return jsonify({
            "success": True,
            "email": email,
            "history": history
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@app.route('/api/save-search', methods=['POST'])
def save_search():
    """Save a search to user's history"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        topic = data.get('topic', '').strip()
        grade = data.get('grade', '')
        
        if not email or not topic:
            return jsonify({
                "success": False,
                "message": "Email and topic are required"
            }), 400
        
        if save_search_history(email, topic, grade):
            return jsonify({
                "success": True,
                "message": "Search saved to history"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to save search"
            }), 500
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "API is running"}), 200

if __name__ == '__main__':
    # Check if database exists, create if not
    if not DB_PATH.exists():
        print("Database not found. Creating...")
        from create_database import create_login_database
        create_login_database()
    
    print(f"Starting API server on http://localhost:5000")
    print(f"Database path: {DB_PATH}")
    app.run(debug=True, port=5000)
