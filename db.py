import aiosqlite
import random
import string
from config import DB_NAME


# ================= INIT =================
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS codes (
            code TEXT PRIMARY KEY
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            user_id INTEGER PRIMARY KEY,
            ref_code TEXT,
            invites INTEGER DEFAULT 0
        )
        """)

        await db.commit()


# ================= USERS =================
async def add_user(uid):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users VALUES (?)", (uid,))
        await db.commit()


async def users_count():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        return (await cur.fetchone())[0]


# ================= CODES =================
async def add_code(code):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO codes VALUES (?)", (code,))
        await db.commit()


async def delete_code(code):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM codes WHERE code=?", (code,))
        await db.commit()


async def get_codes():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT code FROM codes")
        return await cur.fetchall()


# ================= REF =================
async def get_ref(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT ref_code, invites FROM referrals WHERE user_id=?",
            (user_id,)
        )
        return await cur.fetchone()


async def create_ref(user_id):
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=9))

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO referrals VALUES (?,?,0)",
            (user_id, code)
        )
        await db.commit()

    return code


async def set_ref(user_id, code):
    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT 1 FROM referrals WHERE user_id=?",
            (user_id,)
        )

        if await cur.fetchone():
            return False

        cur = await db.execute(
            "SELECT user_id FROM referrals WHERE ref_code=?",
            (code,)
        )
        owner = await cur.fetchone()

        if owner and owner[0] == user_id:
            return False

        await db.execute(
            "INSERT INTO referrals VALUES (?,?,0)",
            (user_id, code)
        )

        await db.execute(
            "UPDATE referrals SET invites = invites + 1 WHERE ref_code=?",
            (code,)
        )

        await db.commit()
        return True
