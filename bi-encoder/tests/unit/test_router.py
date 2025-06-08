from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_encode_endpoint_success():
    response = client.post("/api/encode", params={"chunk": "test"})
    assert response.status_code == 200
    data = response.json()
    assert "vector" in data
    assert isinstance(data["vector"], list)


def test_encode_endpoint_empty_chunk():
    response = client.post("/api/encode", params={"chunk": ""})
    assert response.status_code == 200
    data = response.json()
    assert "vector" in data
    assert isinstance(data["vector"], list)