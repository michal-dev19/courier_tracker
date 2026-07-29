import sqlite3


def get_db():
    conn = sqlite3.connect("courier_tracker.db")
    cursor = conn.cursor()
    try:
        yield conn, cursor
    finally:
        conn.close()
