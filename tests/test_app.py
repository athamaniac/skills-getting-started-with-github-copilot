"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Tests for fetching activities"""

    def test_get_activities_returns_200(self, client):
        """Test that /activities endpoint returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that /activities endpoint returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that activities list contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club",
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity {activity_name} missing field {field}"


class TestSignup:
    """Tests for signing up for activities"""

    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup adds participant to activity"""
        email = "test_add@mergington.edu"
        
        # Sign up for Basketball Team
        response = client.post(
            f"/activities/Basketball%20Team/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities = client.get("/activities").json()
        assert email in activities["Basketball Team"]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for nonexistent activity returns 404"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_already_registered_returns_400(self, client):
        """Test that signing up again returns 400"""
        email = "duplicate@mergington.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/Basketball%20Team/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup (duplicate)
        response2 = client.post(
            f"/activities/Basketball%20Team/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]


class TestUnregister:
    """Tests for unregistering from activities"""

    def test_unregister_successful(self, client):
        """Test successful unregister from an activity"""
        email = "unregister_test@mergington.edu"
        
        # Sign up first
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        # Unregister
        response = client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes participant from activity"""
        email = "remove_test@mergington.edu"
        
        # Sign up for Programming Class
        client.post(f"/activities/Programming%20Class/signup?email={email}")
        
        # Verify participant was added
        activities = client.get("/activities").json()
        assert email in activities["Programming Class"]["participants"]
        
        # Unregister
        client.post(f"/activities/Programming%20Class/unregister?email={email}")
        
        # Verify participant was removed
        activities = client.get("/activities").json()
        assert email not in activities["Programming Class"]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from nonexistent activity returns 404"""
        response = client.post(
            "/activities/NonexistentActivity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_registered_returns_400(self, client):
        """Test that unregistering when not registered returns 400"""
        response = client.post(
            "/activities/Art%20Studio/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestRoot:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
