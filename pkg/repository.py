import time
import sqlite3


def get_db_connection():
    conn = sqlite3.connect('../complaints.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            timestamp INTEGER NOT NULL,
            sentiment TEXT DEFAULT 'unknown',
            category TEXT DEFAULT 'другое'
        )
    ''')
    conn.commit()
    conn.close()


def fetch_complaints_from_db(status, from_time):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, text, status, timestamp, sentiment, category 
        FROM complaints 
        WHERE status = ? AND timestamp >= ?
    ''', (status, from_time))
    rows = cursor.fetchall()
    conn.close()
    return rows


def save_complaint_to_db(complaint_text, sentiment):
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = int(time.time())
    cursor.execute(
        "INSERT INTO complaints (text, sentiment, timestamp) VALUES (?, ?, ?)",
        (complaint_text, sentiment, timestamp)
    )
    complaint_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return complaint_id


def update_category_in_db(category, complaint_id):
    conn = get_db_connection()
    conn.execute("UPDATE complaints SET category = ? WHERE id = ?", (category, complaint_id))
    conn.commit()
    conn.close()


def mark_complaint_as_closed(complaint_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    complaint = cursor.fetchone()
    if not complaint:
        conn.close()
        return False
    cursor.execute("UPDATE complaints SET status = 'closed' WHERE id = ?", (complaint_id,))
    conn.commit()
    conn.close()
    return True
