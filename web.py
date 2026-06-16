from fastapi import FastAPI
import aiosqlite

app = FastAPI()

DB = "db.sqlite3"


@app.get("/")
async def home():
    return {"status": "ok"}


@app.get("/stats")
async def stats():

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT key, value FROM stats")
        data = await cur.fetchall()

    return {
        "stats": dict(data)
    }


@app.get("/users")
async def users():

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        count = await cur.fetchone()

    return {"users": count[0]}


@app.get("/codes")
async def codes():

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT COUNT(*) FROM codes")
        count = await cur.fetchone()

    return {"codes": count[0]}
