import os

import pytest

from db import init_db

os.environ["DATABASE_PATH"] = "test.db"


@pytest.fixture(autouse=True)
def cleanup():
    init_db()
    yield
    if os.path.exists("test.db"):
        os.remove("test.db")
