def _signup_and_login(client, name, email, password="password123"):
    client.post("/auth/signup", json={"name": name, "email": email, "password": password})
    resp = client.post("/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_send_email_lands_in_recipient_inbox(client):
    sender_headers = _signup_and_login(client, "Alice", "alice@example.com")
    _signup_and_login(client, "Bob", "bob@example.com")

    resp = client.post(
        "/emails",
        json={"recipient_email": "bob@example.com", "subject": "Hi", "body": "Hello Bob"},
        headers=sender_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["folder"] == "inbox"
    assert body["is_read"] is False
    assert 0.0 <= body["priority_score"] <= 1.0
    assert body["sender_email"] == "alice@example.com"


def test_recipient_sees_email_in_inbox_sender_sees_in_sent(client):
    sender_headers = _signup_and_login(client, "Alice", "alice@example.com")
    recipient_headers = _signup_and_login(client, "Bob", "bob@example.com")

    client.post(
        "/emails",
        json={"recipient_email": "bob@example.com", "subject": "Hi", "body": "Hello Bob"},
        headers=sender_headers,
    )

    inbox = client.get("/emails", params={"folder": "inbox"}, headers=recipient_headers)
    assert inbox.json()["total"] == 1

    sent = client.get("/emails", params={"folder": "sent"}, headers=sender_headers)
    assert sent.json()["total"] == 1

    # Sender shouldn't see it in their own inbox, recipient shouldn't see it in "sent"
    sender_inbox = client.get("/emails", params={"folder": "inbox"}, headers=sender_headers)
    assert sender_inbox.json()["total"] == 0


def test_search_query_filters_by_subject_or_body(client):
    sender_headers = _signup_and_login(client, "Alice", "alice@example.com")
    recipient_headers = _signup_and_login(client, "Bob", "bob@example.com")

    client.post(
        "/emails",
        json={"recipient_email": "bob@example.com", "subject": "Project update", "body": "..."},
        headers=sender_headers,
    )
    client.post(
        "/emails",
        json={"recipient_email": "bob@example.com", "subject": "Lunch?", "body": "..."},
        headers=sender_headers,
    )

    resp = client.get("/emails", params={"folder": "inbox", "q": "project"}, headers=recipient_headers)
    assert resp.json()["total"] == 1


def test_get_single_email_marks_as_read(client):
    sender_headers = _signup_and_login(client, "Alice", "alice@example.com")
    recipient_headers = _signup_and_login(client, "Bob", "bob@example.com")

    created = client.post(
        "/emails",
        json={"recipient_email": "bob@example.com", "subject": "Hi", "body": "Hello Bob"},
        headers=sender_headers,
    ).json()
    assert created["is_read"] is False

    fetched = client.get(f"/emails/{created['id']}", headers=recipient_headers)
    assert fetched.status_code == 200
    assert fetched.json()["is_read"] is True


def test_get_email_not_yours_returns_404(client):
    sender_headers = _signup_and_login(client, "Alice", "alice@example.com")
    _signup_and_login(client, "Bob", "bob@example.com")
    _signup_and_login(client, "Eve", "eve@example.com")
    eve_headers = _signup_and_login(client, "Eve2", "eve2@example.com")

    created = client.post(
        "/emails",
        json={"recipient_email": "bob@example.com", "subject": "Hi", "body": "Hello Bob"},
        headers=sender_headers,
    ).json()

    resp = client.get(f"/emails/{created['id']}", headers=eve_headers)
    assert resp.status_code == 404


def test_send_to_unknown_recipient_returns_404(client):
    sender_headers = _signup_and_login(client, "Alice", "alice@example.com")
    resp = client.post(
        "/emails",
        json={"recipient_email": "ghost@example.com", "subject": "Hi", "body": "..."},
        headers=sender_headers,
    )
    assert resp.status_code == 404
