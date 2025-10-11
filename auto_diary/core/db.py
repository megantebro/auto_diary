import sqlite3

from ..config import DB_PATH




def connect():
    from ..config import DB_PATH
    print("[DB] connect() →", DB_PATH.resolve())
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn




def init_db():
    with connect() as conn:
        conn.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
        date TEXT PRIMARY KEY,
        body TEXT DEFAULT '',
        ai_generated INTEGER DEFAULT 0,
        created_at TEXT,
        updated_at TEXT
        );
        """
        )