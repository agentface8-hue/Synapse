"""
Tests for health and root endpoints.
"""


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AgentFace API"
    assert data["status"] == "operational"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
