from fastapi.testclient import TestClient
from app import app
client = TestClient(app)
def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_products():
    r = client.get("/products")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3
    assert data[0]["name"] == "Laptop"
