from fastapi.testclient import TestClient

from src.app import app


def test_unregister_participant_removes_participant():
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    original_participants = list(app.activities[activity_name]["participants"])

    try:
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        assert response.status_code == 200
        assert email not in app.activities[activity_name]["participants"]
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
    finally:
        app.activities[activity_name]["participants"] = original_participants
