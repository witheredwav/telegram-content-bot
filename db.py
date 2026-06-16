import sqlite3

conn = sqlite3.connect(
    "bot.db",
    check_same_thread=False
)

cursor = conn.cursor()

# ======================
# КОДЫ
# ======================

cursor.execute("""
CREATE TABLE IF NOT EXISTS codes (
    code TEXT PRIMARY KEY,
    type TEXT,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ======================
# ПОЛЬЗОВАТЕЛИ
# ======================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ======================
# СТАТИСТИКА
# ======================

cursor.execute("""
CREATE TABLE IF NOT EXISTS stats (
    key TEXT PRIMARY KEY,
    value INTEGER
)
""")

conn.commit()


# ======================
# USERS
# ======================

def add_user(user_id):

    cursor.execute(
        """
        INSERT OR IGNORE INTO users(user_id)
        VALUES(?)
        """,
        (user_id,)
    )

    conn.commit()


def get_users_count():

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    return cursor.fetchone()[0]


# ======================
# STATS
# ======================

def increment_stat(key):

    cursor.execute(
        """
        INSERT OR IGNORE INTO stats
        VALUES(?, 0)
        """,
        (key,)
    )

    cursor.execute(
        """
        UPDATE stats
        SET value = value + 1
        WHERE key = ?
        """,
        (key,)
    )

    conn.commit()


def get_stat(key):

    cursor.execute(
        """
        SELECT value
        FROM stats
        WHERE key = ?
        """,
        (key,)
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    return 0


# ======================
# CODES
# ======================

def add_code(
    code,
    type_,
    value
):

    cursor.execute(
        """
        INSERT OR REPLACE INTO codes
        VALUES(
            ?,
            ?,
            ?,
            CURRENT_TIMESTAMP
        )
        """,
        (
            code,
            type_,
            value
        )
    )

    conn.commit()


def get_code(code):

    cursor.execute(
        """
        SELECT type, value
        FROM codes
        WHERE code=?
        """,
        (code,)
    )

    return cursor.fetchone()


def get_all_codes():

    cursor.execute(
        """
        SELECT code, type
        FROM codes
        ORDER BY created_at DESC
        """
    )

    return cursor.fetchall()
