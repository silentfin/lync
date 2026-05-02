import secrets
import string

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import AnyHttpUrl, BaseModel, field_validator

from db import get_connection, init_db

LOWER_ASCII_CHARACTERS = string.ascii_lowercase
UPPER_ASCII_CHARACTERS = string.ascii_uppercase
DIGITS = string.digits

app = FastAPI()
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
    cursor = conn.cursor()
    while True:
        code = "".join(
            secrets.choice(LOWER_ASCII_CHARACTERS + UPPER_ASCII_CHARACTERS + DIGITS)
            for _ in range(5)
        )
        cursor.execute("select 1 from links where short_code = ?", (code,))
        if not cursor.fetchone():
            conn.close()
            return code


@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")


@app.get("/api/links")
def get_all_links():
    conn = get_connection()
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
        conn.close()
        return links
    else:
        return {}


@app.get("/{short_code}")
async def print_url(short_code: str):
    conn = get_connection()
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
        print(f"Found: {url}")
        conn.close()
        return RedirectResponse(url=url)
    else:
        conn.close()
        raise HTTPException(status_code=404, detail="Invalid URL")


@app.post("/")
async def post_url(link: Link):
    print(f"{link.url} is recieved!!!")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "select short_code from links where url = ?",
        (str(link.url),),
    )
    row = cursor.fetchone()
    if row:
        link.short_code = row["short_code"]
        conn.close()
        return link
    else:
        link.short_code = generate_short_code()
        cursor.execute(
            "insert into links (short_code, url) values (?,?)",
            (link.short_code, str(link.url)),
        )
        conn.commit()
        conn.close()
        return link
