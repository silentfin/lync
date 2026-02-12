import json
import secrets
import string

from fastapi import FastAPI
from pydantic import BaseModel

LOWER_ASCII_CHARACTERS = string.ascii_lowercase
UPPER_ASCII_CHARACTERS = string.ascii_uppercase
DIGITS = string.digits

app = FastAPI()


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
    with open("links.json", "r") as f:
        links = json.load(f)
    return links


@app.get("/url/{short_code}")
async def print_url(short_code: str):
    with open("links.json", "r") as f:
        links = json.load(f)
    if short_code in links.keys():
        print(f"Found: {links[short_code]}")
        return links[short_code]
    else:
        return f"NOT FOUND!!!"


@app.post("/url/")
async def post_url(long_url: Link):
    print(f"{long_url.url} is recieved!!!")
    with open("links.json", "r") as f:
        links = json.load(f)
    for short_code, url in links.items():
        if url == long_url.url:
            long_url.short_code = short_code
            return long_url

    long_url.short_code = generate_short_code()
    links[long_url.short_code] = long_url.url
    with open("links.json", "w") as f:
        json.dump(links, f, indent=2)
    return long_url

