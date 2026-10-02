import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def test_activities(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Practice chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["existing@student.test"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(test_activities):
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client, test_activities):
    # Arrange
    expected_activities = test_activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, test_activities):
    # Arrange
    email = "new@student.test"

    # Act
    response = client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in test_activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client, test_activities):
    # Arrange
    email = "existing@student.test"

    # Act
    response = client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert test_activities["Chess Club"]["participants"] == [email]


def test_signup_returns_404_for_unknown_activity(client, test_activities):
    # Arrange
    email = "new@student.test"

    # Act
    response = client.post(
        "/activities/Unknown Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
    assert test_activities["Chess Club"]["participants"] == ["existing@student.test"]


def test_unregister_removes_participant(client, test_activities):
    # Arrange
    email = "existing@student.test"

    # Act
    response = client.delete(
        "/activities/Chess Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert test_activities["Chess Club"]["participants"] == []


def test_unregister_returns_404_for_unknown_activity(client, test_activities):
    # Arrange
    email = "existing@student.test"

    # Act
    response = client.delete(
        "/activities/Unknown Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
    assert test_activities["Chess Club"]["participants"] == [email]


def test_unregister_returns_404_for_unregistered_participant(client, test_activities):
    # Arrange
    email = "unknown@student.test"

    # Act
    response = client.delete(
        "/activities/Chess Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert test_activities["Chess Club"]["participants"] == ["existing@student.test"]