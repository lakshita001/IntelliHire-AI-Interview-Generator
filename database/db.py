import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            email      TEXT    UNIQUE NOT NULL,
            password   TEXT    NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            company_name  TEXT    NOT NULL,
            domain        TEXT    NOT NULL,
            subdomain     TEXT    NOT NULL,
            level         TEXT    NOT NULL,
            num_questions INTEGER NOT NULL,
            date          DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            question     TEXT    NOT NULL,
            answer       TEXT    DEFAULT '',
            score        REAL    DEFAULT 0,
            feedback     TEXT    DEFAULT '',
            FOREIGN KEY (interview_id) REFERENCES interviews(id)
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Tables initialised successfully.")
