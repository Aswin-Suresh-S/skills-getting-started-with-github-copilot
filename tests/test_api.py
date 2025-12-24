import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Deep-copy the activities so tests don't permanently mutate global state
    orig = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(orig)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_duplicate():
    email = "test_student@example.com"
    # Ensure a clean starting state
    if email in activities["Chess Club"]["participants"]:
        activities["Chess Club"]["participants"].remove(email)

    resp = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities["Chess Club"]["participants"]

    # Duplicate signup should fail
    resp2 = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert resp2.status_code == 400


def test_unregister_flow():
    email = "to_remove@example.com"

    # Ensure the participant is present
    if email not in activities["Chess Club"]["participants"]:
        activities["Chess Club"]["participants"].append(email)

    # Unregister should succeed
    resp = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
    assert resp.status_code == 200
    assert email not in activities["Chess Club"]["participants"]

    # Unregistering again should return 404
    resp2 = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
    assert resp2.status_code == 404
