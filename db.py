import logging
import os
import sqlite3

DATABASE_PATH = os.getenv("DATABASE_PATH", "links.db")

logger = logging.getLogger("uvicorn")


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS links(
    short_code TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP,
    click_count INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    logger.info("Initialized Database Successfully.")
    conn.close()
