from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index():
    with TestClient(app) as client:
        response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_available_activities():
    with TestClient(app) as client:
        response = client.get("/activities")

    assert response.status_code == 200
    response_data = response.json()
    assert set(response_data) == {"Chess Club", "Programming Class", "Gym Class"}
    assert response_data["Chess Club"]["max_participants"] == 12
    assert response_data["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_student_and_returns_confirmation():
    with TestClient(app) as client:
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "student@mergington.edu"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up student@mergington.edu for Chess Club"
    }
    assert "student@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_unknown_activity_returns_not_found():
    with TestClient(app) as client:
        response = client.post(
            "/activities/Unknown Club/signup",
            params={"email": "student@mergington.edu"},
        )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_allows_duplicate_email_in_current_behavior():
    email = "michael@mergington.edu"

    with TestClient(app) as client:
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email},
        )

    assert response.status_code == 200
    assert activities["Chess Club"]["participants"].count(email) == 2


def test_signup_accepts_non_email_shaped_value_in_current_behavior():
    with TestClient(app) as client:
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "not-an-email"},
        )

    assert response.status_code == 200
    assert "not-an-email" in activities["Chess Club"]["participants"]


def test_signup_without_email_returns_validation_error():
    with TestClient(app) as client:
        response = client.post("/activities/Chess Club/signup")

    assert response.status_code == 422
