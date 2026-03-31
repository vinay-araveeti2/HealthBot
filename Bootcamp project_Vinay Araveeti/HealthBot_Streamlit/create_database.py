"""
Create SQLite database for user login and search history
"""
import sqlite3
import os
from pathlib import Path

def create_login_database():
    """Create SQLite database with login and search history tables"""
    
    # Database path
    db_path = Path(__file__).parent / "users_database.db"
    
    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ===== LOGIN TABLE =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Login (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add sample login data
    sample_users = [
        ("admin@healthbot.com", "Admin@123", "Admin User"),
        ("user1@example.com", "User@123", "John Doe"),
        ("user2@example.com", "Pass@456", "Jane Smith"),
    ]
    
    for email, password, name in sample_users:
        cursor.execute('''
            INSERT OR IGNORE INTO Login (email_username, password, name)
            VALUES (?, ?, ?)
        ''', (email, password, name))
    
    # ===== SEARCH HISTORY TABLE =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Search_History (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_username TEXT NOT NULL,
            search_topic TEXT NOT NULL,
            date TEXT NOT NULL,
            grade TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (email_username) REFERENCES Login(email_username)
        )
    ''')
    
    # Add sample history data
    sample_history = [
        ("user1@example.com", "Diabetes", "2026-03-20", "A"),
        ("user2@example.com", "Hypertension", "2026-03-21", "B"),
        ("user1@example.com", "Anxiety", "2026-03-22", "A"),
    ]
    
    for email, topic, date, grade in sample_history:
        cursor.execute('''
            INSERT INTO Search_History (email_username, search_topic, date, grade)
            VALUES (?, ?, ?, ?)
        ''', (email, topic, date, grade))
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"✅ Database created successfully at: {db_path}")
    return str(db_path)

if __name__ == "__main__":
    create_login_database()
