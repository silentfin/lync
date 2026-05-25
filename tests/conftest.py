import os

import psycopg
import pytest
from dotenv import load_dotenv

load_dotenv(".env.test", override=True)

from db import init_db


@pytest.fixture(autouse=True)
def cleanup():
    init_db()
    yield
    with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
        conn.execute("DROP TABLE IF EXISTS links")
        conn.commit()
