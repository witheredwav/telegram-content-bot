import aiosqlite
import random
import string
from config import DB_NAME


# =========================
# INIT
# =========================

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes(
            code TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS referrals(
            user_id INTEGER PRIMARY KEY,
            ref_code TEXT UNIQUE,
            invites INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS referral_uses(
            user_id INTEGER PRIMARY KEY,
            owner_id INTEGER,
            code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS stats(
            key TEXT PRIMARY KEY,
            value INTEGER DEFAULT 0
        )
        """)

        await db.commit()


# =========================
# USERS
# =========================

async def add_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users(user_id) VALUES(?)",
            (user_id,)
        )
        await db.commit()


async def users_count():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT COUNT(*) FROM users"
        )
        row = await cur.fetchone()
        return row[0]


# =========================
# PROMO CODES
# =========================

async def create_promo_code():

    code = ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=9
        )
    )

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            "INSERT INTO promo_codes(code) VALUES(?)",
            (code,)
        )

        await db.commit()

    return code


async def get_all_codes():

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT code FROM promo_codes"
        )

        return await cur.fetchall()


async def delete_code(code):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            "DELETE FROM promo_codes WHERE code=?",
            (code,)
        )

        await db.commit()


async def code_exists(code):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT code FROM promo_codes WHERE code=?",
            (code,)
        )

        return await cur.fetchone()


# =========================
# REFERRALS
# =========================

async def get_referral(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            """
            SELECT ref_code, invites
            FROM referrals
            WHERE user_id=?
            """,
            (user_id,)
        )

        return await cur.fetchone()


async def create_ref_code(user_id):

    existing = await get_referral(user_id)

    if existing:
        return existing[0]

    code = ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=9
        )
    )

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT INTO referrals(
                user_id,
                ref_code,
                invites
            )
            VALUES(?,?,0)
            """,
            (
                user_id,
                code
            )
        )

        await db.commit()

    return code


async def use_ref_code(user_id, code):

    async with aiosqlite.connect(DB_NAME) as db:

        # уже использовал
        cur = await db.execute(
            """
            SELECT user_id
            FROM referral_uses
            WHERE user_id=?
            """,
            (user_id,)
        )

        if await cur.fetchone():
            return False

        # ищем владельца
        cur = await db.execute(
            """
            SELECT user_id
            FROM referrals
            WHERE ref_code=?
            """,
            (code,)
        )

        owner = await cur.fetchone()

        if not owner:
            return False

        owner_id = owner[0]

        # защита от самореферала
        if owner_id == user_id:
            return False

        await db.execute(
            """
            INSERT INTO referral_uses(
                user_id,
                owner_id,
                code
            )
            VALUES(?,?,?)
            """,
            (
                user_id,
                owner_id,
                code
            )
        )

        await db.execute(
            """
            UPDATE referrals
            SET invites = invites + 1
            WHERE user_id=?
            """,
            (owner_id,)
        )

        await db.commit()

    return True


async def add_referrals(user_id, amount):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE referrals
            SET invites = invites + ?
            WHERE user_id=?
            """,
            (
                amount,
                user_id
            )
        )

        await db.commit()


async def remove_referrals(user_id, amount):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            """
            SELECT invites
            FROM referrals
            WHERE user_id=?
            """,
            (user_id,)
        )

        row = await cur.fetchone()

        if not row:
            return

        invites = max(0, row[0] - amount)

        await db.execute(
            """
            UPDATE referrals
            SET invites=?
            WHERE user_id=?
            """,
            (
                invites,
                user_id
            )
        )

        await db.commit()


# =========================
# STATS
# =========================

async def inc_stat(key):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT OR IGNORE INTO stats(
                key,
                value
            )
            VALUES(?,0)
            """,
            (key,)
        )

        await db.execute(
            """
            UPDATE stats
            SET value=value+1
            WHERE key=?
            """,
            (key,)
        )

        await db.commit()


async def get_stat(key):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            """
            SELECT value
            FROM stats
            WHERE key=?
            """,
            (key,)
        )

        row = await cur.fetchone()

        return row[0] if row else 0
