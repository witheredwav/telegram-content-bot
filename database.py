import aiosqlite

DB_NAME = "content.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS content(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            text TEXT
        )
        """)

        await db.commit()


async def add_content(title, text):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            "INSERT INTO content(title,text) VALUES(?,?)",
            (title, text)
        )

        await db.commit()


async def get_all_content():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT id,title,text FROM content"
        )

        rows = await cursor.fetchall()

        return rows


async def get_content(content_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT * FROM content WHERE id=?",
            (content_id,)
        )

        return await cursor.fetchone()


async def delete_content(content_id):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            "DELETE FROM content WHERE id=?",
            (content_id,)
        )

        await db.commit()
