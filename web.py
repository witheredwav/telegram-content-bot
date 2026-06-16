from fastapi import FastAPI
import aiosqlite

app = FastAPI()

DB = "db.sqlite3"


@app.get("/")
async def home():
    return {"status": "ok"}
