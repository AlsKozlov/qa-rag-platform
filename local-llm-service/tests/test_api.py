# tests/test_api.py
import unittest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAPI(unittest.TestCase):
    def test_get_answer_success(self):
        payload = {
            "system_msg": "You are a helpful assistant.",
            "user_msg": "Hello!",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 50
        }

        response = client.post("/api/get_answer", json=payload)
        self.assertEqual(response.status_code, 200)