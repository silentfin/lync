import logging
import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "links.db")

logger = logging.getLogger("uvicorn")


def get_connection():
    conn = psycopg.connect(DATABASE_URL)
    conn.row_factory = dict_row
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
