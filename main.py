from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from database import get_db
from auth import get_current_user
from contextlib import asynccontextmanager
from datetime import date
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
        hours_worked REAL,
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


# class for shift creation
class CreateShift(BaseModel):
    hours_worked: float
    earned: int
    mileage: float
    date: date


# returns homepage when "/" is accessed
@app.get("/")
def index():
    return FileResponse("index.html")


# creates a shift for the user
@app.post("/shifts", status_code=201)
def create_shift(
    shift_info: CreateShift, user=Depends(get_current_user), conn_curs=Depends(get_db)
):
    conn, cursor = conn_curs
    try:
        cursor.execute(
            "INSERT INTO shifts (user_id, hours_worked, earned, mileage, date) VALUES (?, ?, ?, ?, ?)",
            (
                user[0],
                shift_info.hours_worked,
                shift_info.earned,
                shift_info.mileage,
                shift_info.date,
            ),
        )
        id = cursor.lastrowid
        if id is None:
            raise HTTPException(status_code=404, detail="Not Found")
        conn.commit()
        return {"shift_id": id}
    except sqlite3.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


# view all shifts for user
@app.get("/shifts")
def all_user_shifts(user=Depends(get_current_user), conn_curs=Depends(get_db)):
    conn, cursor = conn_curs
    try:
        cursor.execute(
            "SELECT id, hours_worked, earned, mileage, date FROM shifts WHERE user_id=?",
            (user[0],),
        )
        shifts = cursor.fetchall()
        if shifts is None:
            raise HTTPException(status_code=404, detail="Not Found")
        return {"all_user_shifts": shifts}
    except sqlite3.Error:
        raise HTTPException(status_code=500, detail="Internal Server Error")


# view specific user shift
@app.post("/shifts/{id}")
def user_shift(id, user=Depends(get_current_user), conn_curs=Depends(get_db)):
    conn, cursor = conn_curs
    try:
        cursor.execute(
            "SELECT hours_worked, earned, mileage, date FROM shifts WHERE id=? AND user_id=?",
            (id, user[0]),
        )
        shift = cursor.fetchone()
        if shift is None:
            raise HTTPException(status_code=404, detail="Not Found")
        return {"shift": shift}
    except sqlite3.Error:
        raise HTTPException(status_code=500, detail="Internal Server Error")
