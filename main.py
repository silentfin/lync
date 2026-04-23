import secrets
import string

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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
    url: str
    short_code: str | None = None


def generate_short_code():
    return "".join(
        secrets.choice(LOWER_ASCII_CHARACTERS + UPPER_ASCII_CHARACTERS + DIGITS)
        for _ in range(5)
    )


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
            }
            for row in rows
        }
        conn.close()
        return links
    else:
        return "NOT FOUND!!"


@app.get("/{short_code}")
async def print_url(short_code: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("select url from links where short_code = ?", (short_code,))
    row = cursor.fetchone()
    if row:
        url = row["url"]
        cursor.execute(
            "UPDATE links SET click_count = click_count + 1 WHERE short_code = ?",
            (short_code,),
        )
        conn.commit()
        print(f"Found: {url}")
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        conn.close()
        return RedirectResponse(url=url)
    else:
        conn.close()
        return {}


@app.post("/")
async def post_url(link: Link):
    print(f"{link.url} is recieved!!!")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("select short_code from links where url = ?", (link.url,))
    row = cursor.fetchone()
    if row:
        link.short_code = row["short_code"]
        conn.close()
        return link
    else:
        link.short_code = generate_short_code()
        cursor.execute(
            "insert into links (short_code, url) values (?,?)",
            (link.short_code, link.url),
        )
        conn.commit()
        conn.close()
        return link
