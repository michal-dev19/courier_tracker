from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from database import get_db
from contextlib import asynccontextmanager
import sqlite3


# initialise the db
def init():
    conn = sqlite3.connect("courier_tracker.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS 
        users
        (id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT)""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS
        shifts
        (id INTEGER PRIMARY KEY,
        user_id INT,
        hours_worked INT,
        earned INT,
        mileage REAL,
        date TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id))""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS
        expenses
        (id INTEGER PRIMARY KEY,
        user_id INT,
        expense_name TEXT,
        total_spent INT,
        date TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id))""")
        conn.commit()
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init()
    yield


app = FastAPI(lifespan=lifespan)


# mounts StaticFiles under /static/ URL for app
app.mount("/static/", StaticFiles(directory="static"))


# returns homepage when "/" is accessed
@app.get("/")
def index():
    return FileResponse("index.html")


######## NEXT SESSION ########
# - build auth.py, register user, login user, authorisation of user
# - then carry on with main endpoints
