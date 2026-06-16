import aiosqlite

DB = "db.sqlite3"


async def init():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            tg_id INTEGER UNIQUE
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS codes (
            code TEXT PRIMARY KEY,
            type TEXT,
            content TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            key TEXT PRIMARY KEY,
            value INTEGER
        )
        """)

        await db.commit()


# -------- USERS --------
async def add_user(tg_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute("INSERT OR IGNORE INTO users VALUES (?)", (tg_id,))
        await db.commit()


async def users_count():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        return (await cur.fetchone())[0]


# -------- STATS --------
async def add_stat(key):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        INSERT INTO stats(key, value)
        VALUES(?, 1)
        ON CONFLICT(key) DO UPDATE SET value = value + 1
        """, (key,))
        await db.commit()


async def get_stats():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT key, value FROM stats")
        return await cur.fetchall()


# -------- CODES --------
async def add_code(code, type_, content):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT OR REPLACE INTO codes VALUES (?, ?, ?)",
            (code, type_, content)
        )
        await db.commit()


async def get_code(code):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT * FROM codes WHERE code=?", (code,))
        return await cur.fetchone()


async def codes_count():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT COUNT(*) FROM codes")
        return (await cur.fetchone())[0]


async def get_all_codes():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT code FROM codes")
        return await cur.fetchall()


async def delete_code_db(code):
    async with aiosqlite.connect(DB) as db:
        await db.execute("DELETE FROM codes WHERE code=?", (code,))
        await db.commit()
