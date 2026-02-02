"""
Tests for agent registration and authentication.
"""


def test_register_agent(client):
    response = client.post(
        "/api/v1/agents/register",
        json={
            "username": "test-agent",
            "display_name": "Test Agent",
            "bio": "A test agent",
            "framework": "pytest",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "test-agent"
    assert "api_key" in data
    assert "access_token" in data
    assert "verification_token" in data


def test_register_duplicate_username(client):
    payload = {
        "username": "duplicate-agent",
        "display_name": "Agent One",
        "bio": "First agent",
        "framework": "pytest",
    }
    client.post("/api/v1/agents/register", json=payload)
    response = client.post("/api/v1/agents/register", json=payload)
    assert response.status_code == 400
    assert "already taken" in response.json()["detail"]


def test_register_invalid_username(client):
    response = client.post(
        "/api/v1/agents/register",
        json={
            "username": "bad name!",
            "display_name": "Bad Agent",
            "framework": "pytest",
        },
    )
    assert response.status_code == 422


def test_register_reserved_username(client):
    response = client.post(
        "/api/v1/agents/register",
        json={
            "username": "admin",
            "display_name": "Admin Agent",
            "framework": "pytest",
        },
    )
    assert response.status_code == 422


def test_get_agent_by_username(client):
    reg = client.post(
        "/api/v1/agents/register",
        json={
            "username": "findme-agent",
            "display_name": "Find Me",
            "framework": "pytest",
        },
    )
    assert reg.status_code == 201

    response = client.get("/api/v1/agents/findme-agent")
    assert response.status_code == 200
    assert response.json()["username"] == "findme-agent"


def test_get_agent_not_found(client):
    response = client.get("/api/v1/agents/nonexistent")
    assert response.status_code == 404


def test_get_current_agent(client):
    reg = client.post(
        "/api/v1/agents/register",
        json={
            "username": "me-agent",
            "display_name": "Me Agent",
            "framework": "pytest",
        },
    )
    token = reg.json()["access_token"]

    response = client.get(
        "/api/v1/agents/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "me-agent"
