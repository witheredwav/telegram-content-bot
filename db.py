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
            action TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            user_id INTEGER PRIMARY KEY,
            code TEXT,
            invites INTEGER DEFAULT 0
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


async def get_all_codes():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT code FROM codes")
        return await cur.fetchall()


async def get_all_codes_full():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT code, content FROM codes")
        return await cur.fetchall()


async def delete_code_db(code):
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
        await db.execute("INSERT INTO stats VALUES (?)", (action,))
        await db.commit()


async def get_stat(action):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT COUNT(*) FROM stats WHERE action=?", (action,))
        return (await cur.fetchone())[0]


# REFERRALS
async def get_all_refs():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT user_id, code, invites FROM referrals")
        return await cur.fetchall()


async def reset_ref(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE referrals SET invites=0 WHERE user_id=?", (user_id,))
        await db.commit()
