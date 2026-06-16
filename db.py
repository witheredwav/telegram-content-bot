import aiosqlite
from config import DB_NAME


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS codes (
            code TEXT PRIMARY KEY,
            content TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            user_id INTEGER PRIMARY KEY,
            code TEXT UNIQUE,
            invites INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS pending_refs (
            user_id INTEGER PRIMARY KEY,
            code TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS ref_logs (
            user_id INTEGER PRIMARY KEY,
            code TEXT
        )
        """)

        await db.commit()


# USERS
async def add_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users VALUES (?)", (user_id,))
        await db.commit()


async def users_count():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        return (await cur.fetchone())[0]


# CODES
async def add_code(code, content):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR REPLACE INTO codes VALUES (?,?)", (code, content))
        await db.commit()


async def get_code(code):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT * FROM codes WHERE code=?", (code,))
        return await cur.fetchone()


async def delete_code(code):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM codes WHERE code=?", (code,))
        await db.commit()


async def codes_count():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT COUNT(*) FROM codes")
        return (await cur.fetchone())[0]


# STATS
async def add_stat(action):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO stats(action) VALUES (?)", (action,))
        await db.commit()


async def get_stat(action):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT COUNT(*) FROM stats WHERE action=?", (action,))
        return (await cur.fetchone())[0]


# REF
async def create_ref(user_id, code):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO referrals VALUES (?,?,0)", (user_id, code))
        await db.commit()


async def get_ref(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT code, invites FROM referrals WHERE user_id=?", (user_id,))
        return await cur.fetchone()


async def get_ref_owner(code):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT user_id FROM referrals WHERE code=?", (code,))
        row = await cur.fetchone()
        return row[0] if row else None


async def add_invite(code):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE referrals SET invites = invites + 1 WHERE code=?", (code,))
        await db.commit()


# pending ref
async def save_pending_ref(user_id, code):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR REPLACE INTO pending_refs VALUES (?,?)", (user_id, code))
        await db.commit()


async def get_pending_ref(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT code FROM pending_refs WHERE user_id=?", (user_id,))
        return await cur.fetchone()


async def clear_pending_ref(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM pending_refs WHERE user_id=?", (user_id,))
        await db.commit()


# ANTI FRAUD
async def ref_exists(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT 1 FROM ref_logs WHERE user_id=?", (user_id,))
        return await cur.fetchone()


async def save_ref_log(user_id, code):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR REPLACE INTO ref_logs VALUES (?,?)", (user_id, code))
        await db.commit()
