def test_signup_creates_user(client):
    resp = client.post(
        "/auth/signup",
        json={"name": "Alice", "email": "alice@example.com", "password": "password123"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert "password" not in body
    assert "password_hash" not in body


def test_signup_duplicate_email_rejected(client):
    payload = {"name": "Alice", "email": "alice@example.com", "password": "password123"}
    client.post("/auth/signup", json=payload)
    resp = client.post("/auth/signup", json=payload)
    assert resp.status_code == 409


def test_login_success_returns_token(client):
    payload = {"name": "Alice", "email": "alice@example.com", "password": "password123"}
    client.post("/auth/signup", json=payload)
    resp = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password_rejected(client):
    payload = {"name": "Alice", "email": "alice@example.com", "password": "password123"}
    client.post("/auth/signup", json=payload)
    resp = client.post("/auth/login", json={"email": payload["email"], "password": "wrongpass"})
    assert resp.status_code == 401


def test_protected_endpoint_requires_token(client):
    resp = client.get("/emails")
    assert resp.status_code == 401
