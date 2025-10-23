import unittest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from mcp_server import app

client = TestClient(app)

class TestMCPServer(unittest.TestCase):
    def test_authorization_check(self):
        payload = {"user_id": "u001", "system": "FinanceApp", "access_level": "Admin"}
        response = client.post("/api/authorization/check", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("authorized", response.json())

    def test_data_lookup(self):
        payload = {"file": "users.csv", "query": {"UserID": "u001"}}
        response = client.post("/api/data/lookup", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.json())

    def test_notify_send(self):
        payload = {"recipient_id": "u001", "subject": "Test", "body": "Test body", "context": {"mutation_id": "1001"}}
        response = client.post("/api/notify/send", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())

    def test_report_generate(self):
        payload = {"mutation_id": "1001", "context": {"findings": {"rights_check": True}}}
        response = client.post("/api/report/generate", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("report_id", response.json())

    def test_root(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())

if __name__ == "__main__":
    unittest.main()