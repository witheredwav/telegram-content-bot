import aiosqlite

DB_NAME = "database.db"

async def create_tables():
async with aiosqlite.connect(DB_NAME) as db:

```
    await db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        first_name TEXT,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        content_type TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        uses INTEGER DEFAULT 0
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS statistics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    await db.commit()
```

async def add_user(
telegram_id,
username,
first_name
):
async with aiosqlite.connect(DB_NAME) as db:

```
    await db.execute(
        """
        INSERT OR IGNORE INTO users
        (
            telegram_id,
            username,
            first_name
        )
        VALUES (?, ?, ?)
        """,
        (
            telegram_id,
            username,
            first_name
        )
    )

    await db.commit()
```

async def add_code(
code,
content_type,
content
):
async with aiosqlite.connect(DB_NAME) as db:

```
    await db.execute(
        """
        INSERT INTO codes
        (
            code,
            content_type,
            content
        )
        VALUES (?, ?, ?)
        """,
        (
            code,
            content_type,
            content
        )
    )

    await db.commit()
```

async def get_code(code):
async with aiosqlite.connect(DB_NAME) as db:

```
    cursor = await db.execute(
        """
        SELECT *
        FROM codes
        WHERE code = ?
        """,
        (code,)
    )

    return await cursor.fetchone()
```

async def increase_code_usage(code):
async with aiosqlite.connect(DB_NAME) as db:

```
    await db.execute(
        """
        UPDATE codes
        SET uses = uses + 1
        WHERE code = ?
        """,
        (code,)
    )

    await db.commit()
```

async def add_stat(action):
async with aiosqlite.connect(DB_NAME) as db:

```
    await db.execute(
        """
        INSERT INTO statistics(action)
        VALUES(?)
        """,
        (action,)
    )

    await db.commit()
```

async def get_users_count():
async with aiosqlite.connect(DB_NAME) as db:

```
    cursor = await db.execute(
        "SELECT COUNT(*) FROM users"
    )

    result = await cursor.fetchone()

    return result[0]
```

async def get_codes_count():
async with aiosqlite.connect(DB_NAME) as db:

```
    cursor = await db.execute(
        "SELECT COUNT(*) FROM codes"
    )

    result = await cursor.fetchone()

    return result[0]
```

async def get_stats_count():
async with aiosqlite.connect(DB_NAME) as db:

```
    cursor = await db.execute(
        "SELECT COUNT(*) FROM statistics"
    )

    result = await cursor.fetchone()

    return result[0]
```
