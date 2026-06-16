import aiosqlite

DB_NAME = "content.db"

async def init_db():

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS codes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            file_id TEXT,
            downloads INTEGER DEFAULT 0
        )
        """)

        await db.commit()


async def add_code(code, file_id):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT OR REPLACE INTO codes
            (code, file_id)
            VALUES (?,?)
            """,
            (code, file_id)
        )

        await db.commit()


async def get_code(code):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT code,file_id,downloads
            FROM codes
            WHERE code=?
            """,
            (code,)
        )

        return await cursor.fetchone()


async def increase_downloads(code):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE codes
            SET downloads = downloads + 1
            WHERE code=?
            """,
            (code,)
        )

        await db.commit()


async def get_all_codes():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT code,downloads
            FROM codes
            """
        )

        return await cursor.fetchall()


async def delete_code(code):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            DELETE FROM codes
            WHERE code=?
            """,
            (code,)
        )

        await db.commit()
