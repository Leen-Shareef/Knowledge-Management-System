# tests/integration/test_api.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# --- TEST 2: API SECURITY ---
def test_unauthorized_access():
    """Fail if trying to chat without a login token."""
    response = client.post("/api/v1/query", json={
        "question": "What is the policy?",
        "session_id": "test-session"
    })
    # Should return 401 Unauthorized
    assert response.status_code == 401

def test_missing_data_validation():
    """Fail if sending an empty payload."""
    # 1. Login to get token
    login_res = client.post("/api/v1/auth/token", data={
        "username": "lolo@kmagent.com", 
        "password": "secret"
    })
    token = login_res.json()["access_token"]
    
    # 2. Send Bad Request (Missing 'question' field)
    response = client.post(
        "/api/v1/query", 
        json={"session_id": "123"}, # Missing 'question'
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # FastAPI returns 422 Unprocessable Entity for missing fields
    assert response.status_code == 422