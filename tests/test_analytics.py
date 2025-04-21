import pytest
from datetime import timedelta
import pytz
from habit_tracker.analytics import *

# Helper Function only for Test
def convert_date_to_utc(date : datetime):
    return date.astimezone(pytz.timezone('UTC'))

# Fixtures to create sample data
@pytest.fixture
def setup_test_data():
    Habit.delete().execute()
    Activity.delete().execute()

    today = datetime.now()

    # Daily habit 1: Longest 5, Current 3
    daily = Habit.create(name="Daily Test", description="A daily habit", frequency="DAILY"  )
    for i in range(5):
        Activity.create(habit=daily, completed_at=convert_date_to_utc(today - timedelta(days=i + 5)))  # 5-day streak in the past
    for i in range(3):
        Activity.create(habit=daily, completed_at=convert_date_to_utc(today - timedelta(days=i)))  # Current 3-day streak

    # Weekly habit 1: Longest 3 Week, Current 2
    weekly = Habit.create(name="Weekly Test", description="A weekly habit", frequency="WEEKLY"  )
    for i in range(3):
        Activity.create(habit=weekly, completed_at=convert_date_to_utc(today - timedelta(weeks=i + 4)))  # 3-week streak in the past
    for i in range(2):
        Activity.create(habit=weekly, completed_at=convert_date_to_utc(today - timedelta(weeks=i)))  # Current 2-week streak

    # Daily Habit 2: Longest 2, No current streak
    broken = Habit.create(name="Broken Daily", description="Has a broken streak", frequency="DAILY")
    for i in [10, 11]:  # two consecutive days long ago
        Activity.create(habit=broken, completed_at=convert_date_to_utc(today - timedelta(days=i)))

    # Weekly Habit 2: No Longest, 1 Current Streak
    single = Habit.create(name="Lonely Weekly", description="Only one weekly entry", frequency="WEEKLY")
    Activity.create(habit=single, completed_at=convert_date_to_utc(today - timedelta(days=3)))  # within current week

    # Daily Habit 3: 7 Day Longest, 7 Day Current
    perfect = Habit.create(name="Perfect Daily", description="Perfect 7-day streak", frequency="DAILY")
    for i in range(7):
        Activity.create(habit=perfect, completed_at=convert_date_to_utc(today - timedelta(days=i)))

    return daily, weekly, broken, single, perfect


import pytest
import pytz
from habit_tracker.analytics import (
    get_streak, list_habits,
    get_most_consistent_habit, get_least_consistent_habit
)

@pytest.mark.parametrize("tz", [
    pytz.UTC,
    pytz.timezone("Asia/Kolkata"),
    pytz.timezone("Europe/London"),
])
def test_get_streak_values(setup_test_data, tz):
    daily, weekly, broken, single, perfect = setup_test_data

    result = get_streak(daily.id, tz=tz)
    assert result["streak"] == 5
    assert result["table"][0][4] == 3
    assert result["table"][0][1] == "Daily Test"

    result = get_streak(weekly.id, tz=tz)
    assert result["streak"] == 3
    assert result["table"][0][4] == 2
    assert result["table"][0][1] == "Weekly Test"

    result = get_streak(broken.id, tz=tz)
    assert result["streak"] == 2
    assert result["table"][0][4] == 0
    assert result["table"][0][1] == "Broken Daily"

    result = get_streak(single.id, tz=tz)
    assert result["streak"] == 1
    assert result["table"][0][4] == 1
    assert result["table"][0][1] == "Lonely Weekly"

    result = get_streak(perfect.id, tz=tz)
    assert result["streak"] == 7
    assert result["table"][0][4] == 7
    assert result["table"][0][1] == "Perfect Daily"


@pytest.mark.parametrize("tz", [
    pytz.UTC,
    pytz.timezone("US/Pacific")
])
def test_get_most_consistent_habit(setup_test_data, tz):
    result = get_most_consistent_habit(tz=tz)
    assert result["most_consistent"] == "Perfect Daily"
    assert result["average_streak"] >= 7


@pytest.mark.parametrize("tz", [
    pytz.UTC,
    pytz.timezone("Europe/Berlin")
])
def test_get_least_consistent_habit(setup_test_data, tz):
    result = get_least_consistent_habit(tz=tz)
    assert result["least_consistent"] == "Lonely Weekly"
    assert result["average_streak"] <= 2


@pytest.mark.parametrize("tz", [
    pytz.UTC,
    pytz.timezone("Australia/Sydney")
])
def test_list_all_habits(setup_test_data, tz):
    result = list_habits(tz=tz)
    habit_names = [row[1] for row in result["table"]]
    assert set(habit_names) == {
        "Daily Test", "Weekly Test", "Broken Daily", "Lonely Weekly", "Perfect Daily"
    }
