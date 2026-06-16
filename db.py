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
        CREATE TABLE IF NOT EXISTS referrals (
            user_id INTEGER PRIMARY KEY,
            ref_code TEXT,
            invites INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            key TEXT PRIMARY KEY,
            value INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS fraud_log (
            user_id INTEGER,
            reason TEXT
        )
        """)

        await db.commit()


# USERS
async def add_user(uid):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users VALUES (?)", (uid,))
        await db.commit()


async def users_count():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        return (await cur.fetchone())[0]


# STATS
async def add_stat(key):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO stats(key,value)
        VALUES (?,1)
        ON CONFLICT(key) DO UPDATE SET value=value+1
        """, (key,))
        await db.commit()


async def get_stat(key):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT value FROM stats WHERE key=?", (key,))
        r = await cur.fetchone()
        return r[0] if r else 0


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


# REF SYSTEM
async def set_ref(user_id, code):
    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute("SELECT 1 FROM referrals WHERE user_id=?", (user_id,))
        if await cur.fetchone():
            return False

        cur = await db.execute("SELECT user_id FROM referrals WHERE ref_code=?", (code,))
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


async def my_ref(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT ref_code, invites FROM referrals WHERE user_id=?", (user_id,))
        return await cur.fetchone()


async def add_invites(user_id, amount):
    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute("SELECT invites FROM referrals WHERE user_id=?", (user_id,))
        row = await cur.fetchone()

        if not row:
            await db.execute("INSERT INTO referrals VALUES (?,?,?)", (user_id, "ADMIN", amount))
        else:
            await db.execute(
                "UPDATE referrals SET invites = invites + ? WHERE user_id=?",
                (amount, user_id)
            )

        await db.commit()


async def remove_invites(user_id, amount):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE referrals SET invites = MAX(invites - ?, 0) WHERE user_id=?",
            (amount, user_id)
        )
        await db.commit()


async def all_refs():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT * FROM referrals")
        return await cur.fetchall()


# FRAUD LOG
async def fraud(uid, reason):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO fraud_log VALUES (?,?)", (uid, reason))
        await db.commit()
