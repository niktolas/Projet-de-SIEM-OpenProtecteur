import uuid


def create_brute_force_alert(client) -> dict:
    for number in range(5):
        response = client.post(
            "/events",
            json={
                "source": "linux_auth",
                "hostname": "srv-linux-01",
                "event_type": "authentication_failure",
                "username": "admin",
                "source_ip": "192.168.50.42",
                "severity": "medium",
                "message": f"Failed authentication {number}",
            },
        )

        assert response.status_code == 201

    response = client.get("/alerts")

    assert response.status_code == 200
    assert response.json()["total"] == 1

    return response.json()["items"][0]


def test_get_alert_by_id(client):
    alert = create_brute_force_alert(client)

    response = client.get(
        f"/alerts/{alert['id']}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == alert["id"]


def test_get_unknown_alert(client):
    response = client.get(
        f"/alerts/{uuid.uuid4()}",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Alert not found",
    }


def test_update_alert_status(client):
    alert = create_brute_force_alert(client)

    response = client.patch(
        f"/alerts/{alert['id']}/status",
        json={
            "status": "investigating",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "investigating"


def test_resolve_alert_under_investigation(client):
    alert = create_brute_force_alert(client)

    first_response = client.patch(
        f"/alerts/{alert['id']}/status",
        json={
            "status": "investigating",
        },
    )

    assert first_response.status_code == 200

    second_response = client.patch(
        f"/alerts/{alert['id']}/status",
        json={
            "status": "resolved",
        },
    )

    assert second_response.status_code == 200
    assert second_response.json()["status"] == "resolved"


def test_reject_invalid_status_value(client):
    alert = create_brute_force_alert(client)

    response = client.patch(
        f"/alerts/{alert['id']}/status",
        json={
            "status": "closed",
        },
    )

    assert response.status_code == 422


def test_reject_invalid_status_transition(client):
    alert = create_brute_force_alert(client)

    resolve_response = client.patch(
        f"/alerts/{alert['id']}/status",
        json={
            "status": "resolved",
        },
    )

    assert resolve_response.status_code == 200

    invalid_response = client.patch(
        f"/alerts/{alert['id']}/status",
        json={
            "status": "false_positive",
        },
    )

    assert invalid_response.status_code == 409
    assert invalid_response.json() == {
        "detail": "Invalid alert status transition",
    }


def test_update_unknown_alert(client):
    response = client.patch(
        f"/alerts/{uuid.uuid4()}/status",
        json={
            "status": "investigating",
        },
    )

    assert response.status_code == 404
