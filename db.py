import sqlite3

conn = sqlite3.connect("codes.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS codes (
    code TEXT PRIMARY KEY,
    type TEXT,
    value TEXT,
    used INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

conn.commit()


def add_user(user_id):
    cur.execute("INSERT OR IGNORE INTO users VALUES (?)", (user_id,))
    conn.commit()


def user_count():
    cur.execute("SELECT COUNT(*) FROM users")
    return cur.fetchone()[0]


def create_code(code, type_, value):
    cur.execute(
        "INSERT OR REPLACE INTO codes VALUES (?, ?, ?, 0)",
        (code, type_, value)
    )
    conn.commit()


def get_code(code):
    cur.execute("SELECT type, value, used FROM codes WHERE code=?", (code,))
    return cur.fetchone()


def mark_used(code):
    cur.execute("UPDATE codes SET used=1 WHERE code=?", (code,))
    conn.commit()
