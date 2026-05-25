import logging
import secrets
import string

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import AnyHttpUrl, BaseModel, field_validator

from db import get_connection, init_db

LOWER_ASCII_CHARACTERS = string.ascii_lowercase
UPPER_ASCII_CHARACTERS = string.ascii_uppercase
DIGITS = string.digits

app = FastAPI()
logger = logging.getLogger("uvicorn")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
init_db()


class Link(BaseModel):
    url: AnyHttpUrl
    short_code: str | None = None

    @field_validator("url", mode="before")
    @classmethod
    def add_https(cls, v):
        if isinstance(v, str) and "://" not in v:
            return f"https://{v}"
        return v


def generate_short_code():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        while True:
            code = "".join(
                secrets.choice(LOWER_ASCII_CHARACTERS + UPPER_ASCII_CHARACTERS + DIGITS)
                for _ in range(5)
            )
            cursor.execute("select 1 from links where short_code = ?", (code,))
            if not cursor.fetchone():
                logger.info(f"Generated short code: {code}")
                return code
    finally:
        conn.close()


@app.get("/")
def read_root():
    logger.info("Serving index.html")
    return FileResponse("static/index.html")


@app.get("/api/links")
def list_links():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("select * from links")
        rows = cursor.fetchall()
        if rows:
            links = {
                row["short_code"]: {
                    "url": row["url"],
                    "created_at": row["created_at"],
                    "click_count": row["click_count"],
                    "last_accessed_at": row["last_accessed_at"],
                }
                for row in rows
            }
            return links
        else:
            return {}
    finally:
        conn.close()


@app.get("/{short_code}")
async def redirect_url(short_code: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("select url from links where short_code = ?", (short_code,))
        row = cursor.fetchone()
        if row:
            url = row["url"]
            cursor.execute(
                "UPDATE links SET click_count = click_count + 1, last_accessed_at = CURRENT_TIMESTAMP WHERE short_code = ?",
                (short_code,),
            )
            conn.commit()
            logger.info(f"Update {url} click_count by 1")
            return RedirectResponse(url=url)
        else:
            logger.warning(f"Short code '{short_code}' not found")
            raise HTTPException(status_code=404, detail="Invalid URL")
    finally:
        conn.close()


@app.get("/{short_code}/stats")
async def get_stats(short_code: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("select * from links where short_code = ?", (short_code,))
        row = cursor.fetchone()
        if row:
            logger.info(f"Serve {short_code} stats")
            return row
        else:
            logger.warning(f"Short code '{short_code}' not found")
            raise HTTPException(status_code=404, detail="Invalid URL")
    finally:
        conn.close()


@app.post("/")
async def shorten_url(link: Link):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "select short_code from links where url = ?",
            (str(link.url),),
        )
        row = cursor.fetchone()
        if row:
            link.short_code = row["short_code"]
            logger.info("URL already exists")
            logger.info(f"Existing short code returned: {link.short_code}")
            return link
        else:
            link.short_code = generate_short_code()
            cursor.execute(
                "insert into links (short_code, url) values (?,?)",
                (link.short_code, str(link.url)),
            )
            conn.commit()
            logger.info(f"New short code returned: {link.short_code}")
            return link
    finally:
        conn.close()
