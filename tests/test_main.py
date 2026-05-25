from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200


def test_shorten_url():
    response = client.post("/", json={"url": "https://duckduckgo.com/"})
    assert response.status_code == 200
    assert "short_code" in response.json()


def test_duplicate_url():
    response1 = client.post("/", json={"url": "https://duckduckgo.com/"})
    response2 = client.post("/", json={"url": "https://duckduckgo.com/"})
    assert response1.json()["short_code"] == response2.json()["short_code"]


def test_invalid_url():
    response = client.post("/", json={"url": "super cool url"})
    assert response.status_code == 422


def test_redirect_url():
    response = client.post("/", json={"url": "https://duckduckgo.com/"})
    short_code = response.json()["short_code"]
    redirect_response = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_response.status_code == 307


def test_invalid_redirect_url():
    response = client.post("/", json={"url": "https://duckduckgo.com/"})
    short_code = response.json()["short_code"]
    invalid_short_code = "lol" + short_code
    redirect_response = client.get(f"/{invalid_short_code}", follow_redirects=False)
    assert redirect_response.status_code == 404


def test_url_stats():
    response = client.post("/", json={"url": "https://duckduckgo.com/"})
    short_code = response.json()["short_code"]
    stats_response = client.get(f"/{short_code}/stats", follow_redirects=False)
    assert stats_response.status_code == 200


def test_invalid_url_stats():
    response = client.post("/", json={"url": "https://duckduckgo.com/"})
    short_code = response.json()["short_code"]
    invalid_short_code = "lol" + short_code
    invalid_stats_response = client.get(
        f"/{invalid_short_code}/stats", follow_redirects=False
    )
    assert invalid_stats_response.status_code == 404


def test_list_links():
    response = client.get("/api/links")
    assert response.status_code == 200
