import aiosqlite

DB = "db.sqlite3"


async def init():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

        await db.commit()


async def add_user(tg_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (tg_id) VALUES (?)",
            (tg_id,)
        )
        await db.commit()


async def add_code(code, type_, content):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT INTO codes VALUES (?, ?, ?)",
            (code, type_, content)
        )
        await db.commit()


async def get_code(code):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT * FROM codes WHERE code=?",
            (code,)
        )
        return await cur.fetchone()


async def users_count():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        return (await cur.fetchone())[0]
