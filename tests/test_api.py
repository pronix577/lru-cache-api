import pytest
import time
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_put_and_get():
    response = client.put("/cache/test_key", json={"value": "test_value"})
    assert response.status_code in (200, 201)
    response = client.get("/cache/test_key")
    assert response.status_code == 200
    assert response.json()["value"] == "test_value"


def test_get_expired():
    response = client.put("/cache/expired_key", json={"value": "value", "ttl": 1})
    time.sleep(2)
    response = client.get("/cache/expired_key")
    assert response.status_code == 404


def test_delete_key():
    response = client.delete("/cache/test_key")
    assert response.status_code == 204
    response = client.get("/cache/test_key")
    assert response.status_code == 404


def test_cache_stats():
    client.put("/cache/stats_key1", json={"value": "value1"})
    client.put("/cache/stats_key2", json={"value": "value2"})
    response = client.get("/cache/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["size"] == 2
    assert stats["capacity"] == 100
    assert "stats_key1" in stats["items"]
    assert "stats_key2" in stats["items"]


def test_capacity_eviction():
    client.delete("/cache/stats_key1")
    client.delete("/cache/stats_key2")

    for i in range(101):
        client.put(f"/cache/key{i}", json={"value": f"value{i}"})
    response = client.get("/cache/stats")
    assert response.json()["size"] == 100
