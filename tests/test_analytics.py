# import pytest
# from datetime import timedelta
# from habit_tracker.analytics import *
# from habit_tracker.services import add_habit
#
# # Fixtures to create sample data
# @pytest.fixture
# def setup_test_data():
#     Habit.delete().execute()
#     Activity.delete().execute()
#
#     today = datetime.now()
#
#     # Daily habit: 3-day streak, 5-day longest
#     daily = Habit.create(name="Daily Test", description="A daily habit", frequency="DAILY")
#     for i in range(5):
#         Activity.create(habit=daily, completed_at=today - timedelta(days=i + 5))  # 5-day streak in the past
#     for i in range(3):
#         Activity.create(habit=daily, completed_at=today - timedelta(days=i))  # Current 3-day streak
#
#     # Weekly habit: 2-week streak, 3-week longest
#     weekly = Habit.create(name="Weekly Test", description="A weekly habit", frequency="WEEKLY")
#     for i in range(3):
#         Activity.create(habit=weekly, completed_at=today - timedelta(weeks=i + 4))  # 3-week streak in the past
#     for i in range(2):
#         Activity.create(habit=weekly, completed_at=today - timedelta(weeks=i))  # Current 2-week streak
#
#     return daily, weekly
#
#
# def test_get_streak_daily(setup_test_data):
#     daily, _ = setup_test_data
#     result = get_streak(daily.id)
#     # Longest Streak
#     assert result["streak"] >= 5
#     # Current Streak
#     assert result["table"][0][4] >= 3
#     assert result["table"][0][1] == "Daily Test"
#
#
# def test_get_streak_weekly(setup_test_data):
#     _, weekly = setup_test_data
#     result = get_streak(weekly.id)
#     # Longest Streak
#     assert result["streak"] >= 3
#     # Current Streak
#     assert result["table"][0][4] >= 2
#     assert result["table"][0][1] == "Weekly Test"
#
#
# def test_get_all_streaks(setup_test_data):
#     result = get_all_streaks()
#     assert "table" in result
#     assert len(result["table"]) == 2
#     for row in result["table"]:
#         assert row[0]  # habit_id
#         assert row[1] in ["Daily Test", "Weekly Test"]
#         assert row[4] >= 0  # current streak
#         assert row[5] >= 0  # longest streak
#
#
# def test_list_habits_all(setup_test_data):
#     result = list_habits()
#     assert len(result) == 2
#     names = [row[1] for row in result]
#     assert "Daily Test" in names
#     assert "Weekly Test" in names
#
#
# def test_list_habits_daily_only(setup_test_data):
#     result = list_habits(frequency="DAILY")
#     assert len(result) == 1
#     assert result[0][1] == "Daily Test"
#
#
# def test_list_habits_weekly_only(setup_test_data):
#     result = list_habits(frequency="WEEKLY")
#     assert len(result) == 1
#     assert result[0][1] == "Weekly Test"
#
#
# def test_get_most_consistent_habit(setup_test_data):
#     result = get_most_consistent_habit()
#     assert "most_consistent" in result
#     assert result["average_streak"] >= 0
#     assert result["most_consistent"] in ["Daily Test", "Weekly Test"]
#
#
# def test_get_least_consistent_habit(setup_test_data):
#     result = get_least_consistent_habit()
#     assert "least_consistent" in result
#     assert result["average_streak"] >= 0
#     assert result["least_consistent"] in ["Daily Test", "Weekly Test"]


import pytest
from datetime import timedelta
from datetime import datetime
import pytz
from habit_tracker.analytics import *
from habit_tracker.services import add_habit


# Fixtures to create sample data
@pytest.fixture
def setup_test_data():
    Habit.delete().execute()
    Activity.delete().execute()

    today = datetime.now()

    # Daily habit: 3-day streak, 5-day longest
    daily = Habit.create(name="Daily Test", description="A daily habit", frequency="DAILY")
    for i in range(5):
        Activity.create(habit=daily, completed_at=today - timedelta(days=i + 5))  # 5-day streak in the past
    for i in range(3):
        Activity.create(habit=daily, completed_at=today - timedelta(days=i))  # Current 3-day streak

    # Weekly habit: 2-week streak, 3-week longest
    weekly = Habit.create(name="Weekly Test", description="A weekly habit", frequency="WEEKLY")
    for i in range(3):
        Activity.create(habit=weekly, completed_at=today - timedelta(weeks=i + 4))  # 3-week streak in the past
    for i in range(2):
        Activity.create(habit=weekly, completed_at=today - timedelta(weeks=i))  # Current 2-week streak

    return daily, weekly


def test_get_streak_daily(setup_test_data):
    daily, _ = setup_test_data
    tz_utc = pytz.timezone("UTC")
    tz_eastern = pytz.timezone("US/Eastern")

    # Test UTC timezone (default behavior)
    result_utc = get_streak(daily.id, tz=tz_utc)
    assert result_utc["streak"] >= 5
    assert result_utc["table"][0][4] >= 3
    assert result_utc["table"][0][1] == "Daily Test"

    # Test non-UTC timezone (Eastern)
    result_eastern = get_streak(daily.id, tz=tz_eastern)
    assert result_eastern["streak"] >= 5
    assert result_eastern["table"][0][4] >= 3
    assert result_eastern["table"][0][1] == "Daily Test"


def test_get_streak_weekly(setup_test_data):
    _, weekly = setup_test_data
    tz_utc = pytz.timezone("UTC")
    tz_eastern = pytz.timezone("US/Eastern")

    # Test UTC timezone (default behavior)
    result_utc = get_streak(weekly.id, tz=tz_utc)
    assert result_utc["streak"] >= 3
    assert result_utc["table"][0][4] >= 2
    assert result_utc["table"][0][1] == "Weekly Test"

    # Test non-UTC timezone (Eastern)
    result_eastern = get_streak(weekly.id, tz=tz_eastern)
    assert result_eastern["streak"] >= 3
    assert result_eastern["table"][0][4] >= 2
    assert result_eastern["table"][0][1] == "Weekly Test"


def test_get_all_streaks(setup_test_data):
    tz_utc = pytz.timezone("UTC")
    tz_eastern = pytz.timezone("US/Eastern")

    # Test UTC timezone (default behavior)
    result_utc = get_all_streaks(tz=tz_utc)
    assert "table" in result_utc
    assert len(result_utc["table"]) == 2
    for row in result_utc["table"]:
        assert row[0]  # habit_id
        assert row[1] in ["Daily Test", "Weekly Test"]
        assert row[4] >= 0  # current streak
        assert row[5] >= 0  # longest streak

    # Test non-UTC timezone (Eastern)
    result_eastern = get_all_streaks(tz=tz_eastern)
    assert "table" in result_eastern
    assert len(result_eastern["table"]) == 2
    for row in result_eastern["table"]:
        assert row[0]  # habit_id
        assert row[1] in ["Daily Test", "Weekly Test"]
        assert row[4] >= 0  # current streak
        assert row[5] >= 0  # longest streak


def test_list_habits_all(setup_test_data):
    tz_utc = pytz.timezone("UTC")
    tz_eastern = pytz.timezone("US/Eastern")

    # Test UTC timezone (default behavior)
    result_utc = list_habits(tz=tz_utc)
    assert len(result_utc["table"]) == 2  # Expecting two habits (Daily and Weekly)
    names_utc = [row[1] for row in result_utc["table"]]
    assert "Daily Test" in names_utc
    assert "Weekly Test" in names_utc

    # Test non-UTC timezone (Eastern)
    result_eastern = list_habits(tz=tz_eastern)
    assert len(result_eastern["table"]) == 2  # Expecting two habits (Daily and Weekly)
    names_eastern = [row[1] for row in result_eastern["table"]]
    assert "Daily Test" in names_eastern
    assert "Weekly Test" in names_eastern


def test_get_most_consistent_habit(setup_test_data):
    tz_utc = pytz.timezone("UTC")
    tz_eastern = pytz.timezone("US/Eastern")

    # Test UTC timezone (default behavior)
    result_utc = get_most_consistent_habit(tz=tz_utc)
    assert "most_consistent" in result_utc
    assert result_utc["average_streak"] >= 0
    assert result_utc["most_consistent"] in ["Daily Test", "Weekly Test"]

    # Test non-UTC timezone (Eastern)
    result_eastern = get_most_consistent_habit(tz=tz_eastern)
    assert "most_consistent" in result_eastern
    assert result_eastern["average_streak"] >= 0
    assert result_eastern["most_consistent"] in ["Daily Test", "Weekly Test"]


def test_get_least_consistent_habit(setup_test_data):
    tz_utc = pytz.timezone("UTC")
    tz_eastern = pytz.timezone("US/Eastern")

    # Test UTC timezone (default behavior)
    result_utc = get_least_consistent_habit(tz=tz_utc)
    assert "least_consistent" in result_utc
    assert result_utc["average_streak"] >= 0
    assert result_utc["least_consistent"] in ["Daily Test", "Weekly Test"]

    # Test non-UTC timezone (Eastern)
    result_eastern = get_least_consistent_habit(tz=tz_eastern)
    assert "least_consistent" in result_eastern
    assert result_eastern["average_streak"] >= 0
    assert result_eastern["least_consistent"] in ["Daily Test", "Weekly Test"]
