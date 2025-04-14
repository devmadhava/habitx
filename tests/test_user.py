import pytest
from datetime import datetime
from habit_tracker.user import *
from habit_tracker.models import Config

@pytest.fixture
def sample_user():
    config = Config.create(username="test_user", timezone="UTC", color="#ffffff", updated_at=datetime.utcnow())
    return config

def test_get_display_timezone(sample_user):
    response = get_display_timezone()
    assert response == {"timezone": "UTC"}

def test_set_display_timezone_valid(sample_user):
    response = set_display_timezone("Asia/Kolkata")
    assert response == {"success": "Timezone updated to 'Asia/Kolkata'"}
    assert Config.get().timezone == "Asia/Kolkata"

def test_set_display_timezone_invalid(sample_user):
    response = set_display_timezone("Invalid/Zone")
    assert response == {"success": "Timezone updated to 'UTC'"}
    assert Config.get().timezone == "UTC"

def test_get_username(sample_user):
    response = get_username()
    assert response == {"username": "test_user"}

def test_set_username(sample_user):
    response = set_username("new_user")
    assert response == {"success": "Username updated to 'new_user'"}
    assert Config.get().username == "new_user"

def test_get_user_color(sample_user):
    response = get_user_color()
    assert response == {"color": "#ffffff"}

def test_set_user_color(sample_user):
    response = set_user_color("#123456")
    assert response == {"success": "Color updated to '#123456'"}
    assert Config.get().color == "#123456"

def test_get_user_config(sample_user):
    response = get_user_config()
    assert response == {
        "username": "test_user",
        "timezone": "UTC",
        "color": "#ffffff"
    }

def test_set_user_config_all_fields(sample_user):
    response = set_user_config(username="combo", timezone="Asia/Kolkata", color="#ffcc00")
    print(response)
    assert "success" in response
    assert response["success"] == {
        "username": "combo",
        "timezone": "Asia/Kolkata",
        "color": "#ffcc00"
    }

def test_set_user_config_partial_update(sample_user):
    response = set_user_config(username="partial_user")
    print(response)
    assert response["success"] == {
        "username": "partial_user",
    }
    assert Config.get().username == "partial_user"

def test_set_user_config_no_update(sample_user):
    response = set_user_config()
    assert response == {"warning": "No fields were updated because no values were provided."}
