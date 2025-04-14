import pytest
from datetime import datetime, timedelta
from habit_tracker.services import *

@pytest.fixture
def sample_habit():
    habit = Habit.create(name="Test Habit", description="Testing", frequency="DAILY")
    return habit

def test_add_habit():
    response = add_habit("Test", "Test Desc", "DAILY")
    assert "table" in response
    assert response["table"][0][1] == "Test"
    assert response["table"][0][2] == "Test Desc"

def test_get_habit(sample_habit):
    response = get_habit(sample_habit.id)
    assert "table" in response
    assert response["table"][0][1] == "Test Habit"

def test_edit_habit(sample_habit):
    response = edit_habit(sample_habit.id, "Edited", "Edited Desc")
    assert "table" in response
    assert response["table"][0][1] == "Edited"
    assert response["table"][0][2] == "Edited Desc"

def test_mark_completed(sample_habit):
    response = mark_completed(sample_habit.id)
    assert "success" in response

def test_unmark_completed(sample_habit):
    mark_completed(sample_habit.id)
    response = unmark_completed(sample_habit.id)
    assert "success" in response

def test_delete_habit(sample_habit):
    response = delete_habit(sample_habit.id)
    assert "success" in response
    assert Habit.get_or_none(Habit.id == sample_habit.id) is None

def test_get_active_habits_by_date(sample_habit):
    mark_completed(sample_habit.id)
    today_str = datetime.utcnow().strftime('%d.%m.%Y')
    response = get_active_habits_by_date(today_str)
    assert "table" in response or "error" not in response