import aiosqlite

DB_NAME = "bot.db"


# ================= INIT DB =================
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
        CREATE TABLE IF NOT EXISTS events (
            user_id INTEGER,
            event TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            user_id INTEGER PRIMARY KEY,
            code TEXT,
            invites INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS discounts (
            user_id INTEGER PRIMARY KEY,
            percent INTEGER DEFAULT 0
        )
        """)

        await db.commit()


# ================= USERS =================
async def add_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users VALUES (?)",
            (user_id,)
        )
        await db.commit()


async def users_count():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        return (await cur.fetchone())[0]


# ================= CODES =================
async def add_code(code, content):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO codes VALUES (?,?)",
            (code, content)
        )
        await db.commit()


async def get_code(code):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT * FROM codes WHERE code=?",
            (code,)
        )
        return await cur.fetchone()


async def get_all_codes_full():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT code, content FROM codes")
        return await cur.fetchall()


async def delete_code_db(code):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM codes WHERE code=?",
            (code,)
        )
        await db.commit()


async def codes_count():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT COUNT(*) FROM codes")
        return (await cur.fetchone())[0]


# ================= EVENTS =================
async def add_event(user_id, event):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO events VALUES (?,?)",
            (user_id, event)
        )
        await db.commit()


# ================= REF SYSTEM =================
async def add_ref_if_valid(user_id: int, code: str):
    async with aiosqlite.connect(DB_NAME) as db:

        # уже использовал реф
        cur = await db.execute(
            "SELECT 1 FROM referrals WHERE user_id=?",
            (user_id,)
        )
        if await cur.fetchone():
            return False

        # владелец кода
        cur = await db.execute(
            "SELECT user_id FROM referrals WHERE code=?",
            (code,)
        )
        owner = await cur.fetchone()

        if owner and owner[0] == user_id:
            return False

        await db.execute(
            "INSERT INTO referrals(user_id, code, invites) VALUES (?,?,0)",
            (user_id, code)
        )

        await db.execute(
            "UPDATE referrals SET invites = invites + 1 WHERE code=?",
            (code,)
        )

        await db.commit()
        return True


async def update_ref_level(user_id):
    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT invites FROM referrals WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()

        if not row:
            return 0

        invites = row[0]

        if invites >= 20:
            percent = 20
        elif invites >= 10:
            percent = 15
        elif invites >= 5:
            percent = 10
        else:
            percent = 0

        await db.execute("""
        INSERT INTO discounts(user_id, percent)
        VALUES (?,?)
        ON CONFLICT(user_id) DO UPDATE SET percent=excluded.percent
        """, (user_id, percent))

        await db.commit()
        return percent


# ================= ADMIN REF =================
async def add_invites(user_id: int, amount: int):
    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT invites FROM referrals WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()

        if not row:
            await db.execute(
                "INSERT INTO referrals(user_id, code, invites) VALUES (?,?,?)",
                (user_id, "ADMIN", amount)
            )
        else:
            await db.execute(
                "UPDATE referrals SET invites = invites + ? WHERE user_id=?",
                (amount, user_id)
            )

        await db.commit()
