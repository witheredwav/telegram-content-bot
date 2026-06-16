import sqlite3

conn = sqlite3.connect("codes.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS codes (
    code TEXT PRIMARY KEY,
    type TEXT,
    value TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

conn.commit()


def add_code(code, type_, value):
    cursor.execute(
        "INSERT OR REPLACE INTO codes VALUES (?, ?, ?)",
        (code, type_, value)
    )
    conn.commit()


def get_code(code):
    cursor.execute("SELECT type, value FROM codes WHERE code=?", (code,))
    return cursor.fetchone()


def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?)", (user_id,))
    conn.commit()


def count_users():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]
