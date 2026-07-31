import sqlite3


def get_db():
    # we connect to our database and obtain the cursor to navigate it
    conn = sqlite3.connect("courier_tracker.db")
    cursor = conn.cursor()
    # try block to yield conn and cursor (operations freeze after yield)
    try:
        yield conn, cursor
    # once conn and cursor is no longer in use, or an error occurs at any point,
    # the finally block ensures connection always closes
    finally:
        conn.close()
