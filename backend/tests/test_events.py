import uuid


def build_event_payload(
    *,
    hostname: str = "srv-linux-01",
    severity: str = "medium",
) -> dict:
    return {
        "source": "linux_auth",
        "hostname": hostname,
        "event_type": "authentication_failure",
        "username": "admin",
        "source_ip": "192.168.1.42",
        "severity": severity,
        "message": "Failed SSH authentication",
    }


def test_create_security_event(client):
    response = client.post(
        "/events",
        json=build_event_payload(),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["hostname"] == "srv-linux-01"
    assert body["severity"] == "medium"
    assert body["event_type"] == "authentication_failure"
    assert "id" in body
    assert "created_at" in body


def test_reject_invalid_ip_address(client):
    payload = build_event_payload()
    payload["source_ip"] = "999.999.999.999"

    response = client.post(
        "/events",
        json=payload,
    )

    assert response.status_code == 422


def test_list_security_events_with_pagination(client):
    for index in range(3):
        client.post(
            "/events",
            json=build_event_payload(
                hostname=f"srv-linux-{index}",
            ),
        )

    response = client.get(
        "/events",
        params={
            "limit": 2,
            "offset": 0,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 3
    assert body["limit"] == 2
    assert body["offset"] == 0
    assert body["returned"] == 2
    assert len(body["items"]) == 2


def test_filter_security_events_by_severity(client):
    client.post(
        "/events",
        json=build_event_payload(
            hostname="srv-low",
            severity="low",
        ),
    )

    client.post(
        "/events",
        json=build_event_payload(
            hostname="srv-high",
            severity="high",
        ),
    )

    response = client.get(
        "/events",
        params={
            "severity": "high",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["items"][0]["hostname"] == "srv-high"
    assert body["items"][0]["severity"] == "high"


def test_get_security_event_by_id(client):
    create_response = client.post(
        "/events",
        json=build_event_payload(),
    )

    event_id = create_response.json()["id"]

    response = client.get(
        f"/events/{event_id}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == event_id


def test_get_unknown_security_event(client):
    unknown_id = uuid.uuid4()

    response = client.get(
        f"/events/{unknown_id}",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Security event not found",
    }


def test_delete_security_event(client):
    create_response = client.post(
        "/events",
        json=build_event_payload(),
    )

    event_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/events/{event_id}",
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/events/{event_id}",
    )

    assert get_response.status_code == 404
