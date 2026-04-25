import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """Fixture to provide a test client with isolated app state."""
    original_activities = copy.deepcopy(activities)
    test_client = TestClient(app)
    yield test_client
    # Reset activities after each test
    activities.clear()
    activities.update(original_activities)


def test_root_redirect():
    """Test that root endpoint redirects to static index.html."""
    # Arrange
    client = TestClient(app, follow_redirects=False)

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test retrieving all activities."""
    # Arrange
    # (client fixture handles setup)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_success(client):
    """Test successful signup for an activity."""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    # Verify participant was added
    response_check = client.get("/activities")
    activities_data = response_check.json()
    assert email in activities_data[activity_name]["participants"]


def test_signup_already_signed_up(client):
    """Test signup when student is already signed up."""
    # Arrange
    activity_name = "Chess Club"
    email = "existing@mergington.edu"
    # First signup
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_activity_not_found(client):
    """Test signup for a non-existent activity."""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_success(client):
    """Test successful removal of a participant from an activity."""
    # Arrange
    activity_name = "Programming Class"
    email = "removeme@mergington.edu"
    # First signup
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    # Verify participant was removed
    response_check = client.get("/activities")
    activities_data = response_check.json()
    assert email not in activities_data[activity_name]["participants"]


def test_remove_participant_not_found(client):
    """Test removal when participant is not signed up."""
    # Arrange
    activity_name = "Gym Class"
    email = "notsigned@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found in this activity"}


def test_remove_activity_not_found(client):
    """Test removal from a non-existent activity."""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}