import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_for_activity():
    # Test successful signup
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

    # Verify the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Chess Club"]["participants"]

def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Soccer%20Club/signup?email=duplicate@example.com")
    
    # Try to signup again
    response = client.post("/activities/Soccer%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]

def test_signup_nonexistent_activity():
    response = client.post("/activities/Nonexistent/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_from_activity():
    # First signup
    client.post("/activities/Basketball%20Team/signup?email=unregister@example.com")
    
    # Then unregister
    response = client.delete("/activities/Basketball%20Team/participants/unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

    # Verify the participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@example.com" not in data["Basketball Team"]["participants"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Art%20Club/participants/notsigned@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]

def test_unregister_nonexistent_activity():
    response = client.delete("/activities/Nonexistent/participants/test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Redirect
    assert "/static/index.html" in response.headers["location"]