from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_get_top_hanja():
    response = client.get("/analysis/hanja?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) <= 10
    assert data["page"] == 1
    assert data["size"] == 10
    
    if len(data["items"]) > 0:
        item = data["items"][0]
        assert "hanja" in item
        assert "frequency" in item
        assert "char" in item["hanja"]
        assert "readings" in item["hanja"]

def test_get_top_radicals():
    response = client.get("/analysis/radicals?page=1&size=5")
    assert response.status_code == 200
    data = response.json()
    
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) <= 5
    
    if len(data["items"]) > 0:
        item = data["items"][0]
        assert "radical" in item
        assert "frequency" in item

def test_get_top_word_chars():
    response = client.get("/analysis/words/chars?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) <= 10
    
    if len(data["items"]) > 0:
        item = data["items"][0]
        assert "char" in item
        assert "frequency" in item
        assert "hanja_info" in item

def test_pagination():
    # Request page 1
    response1 = client.get("/analysis/hanja?page=1&size=5")
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Request page 2
    response2 = client.get("/analysis/hanja?page=2&size=5")
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Ensure items are different (assuming we have enough data)
    if data1["total"] > 5:
        assert data1["items"][0]["hanja"]["id"] != data2["items"][0]["hanja"]["id"]
