"""
Module for handling habit streak calculations and related operations.

This module provides helper functions and service functions for tracking and calculating
streaks of habit completions (daily/weekly), considering the user's timezone. It uses the
Peewee ORM to interact with the Habit and Activity models. Key functionalities include getting
the longest streak, current streak, average streaks, and fetching streak data for specific
habits or all habits.

Helper functions also support operations like formatting date strings, calculating streaks based
on local calendar days or weeks, and handling database errors.

Imports:
    datetime (datetime): For working with date and time.
    peewee (fn, DatabaseError, IntegrityError): For working with the Peewee ORM and handling database errors.
    habit_tracker.models (Habit, Activity): Models for habit tracking and activity data.
    habit_tracker.utils (convert_user_date_str_to_iso, database_error_handler, get_current_utc_time, parse_iso_datetime):
        Utility functions for date conversion, error handling, and formatting.

Functions:
    _get_habit_by_id(habit_id): Retrieve a habit by its ID with consistent error handling.
    _get_longest_daily_streak(completed_dates): Calculate the longest streak of daily habit completions.
    _get_longest_weekly_streak(completed_dates): Calculate the longest streak of weekly habit completions.
    _get_current_daily_streak(completed_dates): Calculate the current streak of daily habit completions.
    _get_current_weekly_streak(completed_dates): Calculate the current streak of weekly habit completions.
    _get_average_daily_streak(completed_dates): Calculate the average daily streak for a habit.
    _get_average_weekly_streak(completed_dates): Calculate the average weekly streak for a habit.
    get_streak(habit_id, tz): Retrieve the streak (longest and current) for a specific habit, with optional timezone support.
    get_all_streaks(tz): Retrieve streak data for all habits, with optional timezone support.
    list_habits(frequency=None, created_at=None, completed_at=None, timezone): List all habits with optional filters for frequency, creation date, or last completion date.
    get_most_consistent_habit(tz): Get the habit with the highest average streak, considering the user's timezone.
    get_least_consistent_habit(tz): Get the habit with the lowest average streak, considering the user's timezone.
"""


from datetime import datetime
import pytz
from peewee import fn
from habit_tracker.models import Habit, Activity
from habit_tracker.utils import database_error_handler, date_str_to_utc_iso, convert_iso_to_date


def _get_habit_by_id(habit_id):
    """
    Retrieve a habit from the database by its ID.

    Args:
        habit_id (int): The ID of the habit to retrieve.

    Returns:
        dict: A dictionary containing the habit details or None if the habit does not exist.
            {
                "id": int,
                "name": str,
                "created_at": str,  # Date in 'dd-mm-yyyy' format
                "last_completed_at": str or None,  # Date in 'dd-mm-yyyy' format or None
                "frequency": str  # 'DAILY' or 'WEEKLY'
            }

    Example:
        _get_habit_by_id(1)
        Returns: {
            "id": 1,
            "name": "Exercise",
            "created_at": "01-01-2021",
            "last_completed_at": "05-01-2021",
            "frequency": "DAILY"
        }
    """
    habit = list(Habit.select(
        Habit.id,
        Habit.name,
        Habit.created_at,
        Habit.last_completed_at,
        Habit.frequency
    ).where(Habit.id == habit_id))[0]
    return habit


def _get_longest_daily_streak(completed_dates, tz: pytz.tzinfo):
    """
    Calculate the longest daily streak using calendar-day logic in the user's timezone.

    Args:
        completed_dates (list of datetime): A list of UTC datetime objects representing completion dates.
        tz (pytz.tzinfo): User's timezone.

    Returns:
        int: The length of the longest daily streak, based on calendar days in the user's timezone.

    Example:
        _get_longest_daily_streak([
            datetime(2025, 4, 1, 14, 0, tzinfo=pytz.UTC),
            datetime(2025, 4, 2, 16, 0, tzinfo=pytz.UTC),
            datetime(2025, 4, 4, 9, 0, tzinfo=pytz.UTC)
        ], pytz.timezone('America/New_York'))
        Returns: 2  # Streak is from 2025-04-01 to 2025-04-02 in the user's timezone.
    """
    if not completed_dates:
        return 0

    # Convert all UTC datetimes to user's local calendar dates
    local_dates = [dt.astimezone(tz).date() for dt in completed_dates]
    local_dates = sorted(set(local_dates))  # Remove duplicates and sort

    longest_streak = 1
    current_streak = 1

    for i in range(1, len(local_dates)):
        if (local_dates[i] - local_dates[i - 1]).days == 1:
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 1

    return longest_streak


def _get_longest_weekly_streak(completed_dates, tz: pytz.tzinfo):
    """
    Calculate the longest weekly streak using calendar-week logic in the user's timezone.

    Args:
        completed_dates (list of datetime): A list of UTC datetime objects representing completion dates.
        tz (pytz.tzinfo): User's timezone.

    Returns:
        int: The length of the longest weekly streak, based on calendar weeks in the user's timezone.

    Example:
        _get_longest_weekly_streak([
            datetime(2025, 4, 1, 14, 0, tzinfo=pytz.UTC),
            datetime(2025, 4, 8, 10, 0, tzinfo=pytz.UTC),
            datetime(2025, 4, 15, 16, 0, tzinfo=pytz.UTC)
        ], pytz.timezone('America/New_York'))
        Returns: 3  # Streak is from the week of 2025-03-30 to 2025-04-12 in the user's timezone.
    """
    if not completed_dates:
        return 0

    # Convert UTC datetimes to user-local dates, then to (year, week number)
    local_weeks = [dt.astimezone(tz).isocalendar()[:2] for dt in completed_dates]
    local_weeks = sorted(set(local_weeks))  # Remove duplicates and sort

    longest_streak = 1
    current_streak = 1

    for i in range(1, len(local_weeks)):
        prev_year, prev_week = local_weeks[i - 1]
        curr_year, curr_week = local_weeks[i]

        # Handle year change
        if (curr_year == prev_year and curr_week == prev_week + 1) or \
           (curr_year == prev_year + 1 and prev_week == 52 and curr_week == 1):
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 1

    return longest_streak


def _get_current_daily_streak(completed_dates, user_tz):
    """
    Calculate the current daily streak based on local calendar days.

    Args:
        completed_dates (list of datetime): UTC datetimes of completions.
        user_tz (pytz.timezone): User's timezone.

    Returns:
        int: Current daily streak count.
    """
    if not completed_dates:
        return 0

    # Convert all to user-local calendar dates
    local_dates = [dt.astimezone(user_tz).date() for dt in completed_dates]
    today = datetime.now(user_tz).date()
    # today = datetime.now(user_tz).astimezone(user_tz).date()

    if local_dates[-1] != today:
        return 0

    streak = 1
    for i in range(len(local_dates) - 1, 0, -1):
        if (local_dates[i] - local_dates[i - 1]).days == 1:
            streak += 1
        elif local_dates[i] == local_dates[i - 1]:
            continue
        else:
            break

    return streak


def _get_current_weekly_streak(completed_dates, user_tz):
    """
    Calculate the current daily streak based on local calendar days in the user's timezone.

    Args:
        completed_dates (list of datetime): A list of UTC datetime objects representing habit completion dates.
        user_tz (pytz.timezone): User's timezone.

    Returns:
        int: The current streak length based on local calendar days in the user's timezone.

    Example:
        _get_current_daily_streak([
            datetime(2025, 4, 1, 14, 0, tzinfo=pytz.UTC),
            datetime(2025, 4, 2, 16, 0, tzinfo=pytz.UTC)
        ], pytz.timezone('America/New_York'))
        Returns: 2  # Streak is from 2025-04-01 to 2025-04-02 in the user's timezone.
    """
    if not completed_dates:
        return 0

    # Convert to user-local weekly identifiers (year, week number)
    local_weeks = [
        dt.astimezone(user_tz).isocalendar()[:2] for dt in completed_dates
    ]
    current_week = datetime.now(user_tz).isocalendar()[:2]

    if local_weeks[-1] != current_week:
        return 0

    streak = 1
    for i in range(len(local_weeks) - 1, 0, -1):
        prev_year, prev_week = local_weeks[i - 1]
        curr_year, curr_week = local_weeks[i]

        # Check if weeks are consecutive
        if (curr_year == prev_year and curr_week - prev_week == 1) or \
           (curr_year - prev_year == 1 and prev_week == 52 and curr_week == 1):
            streak += 1
        else:
            break

    return streak


def _get_average_daily_streak(completed_dates, user_tz):
    """
    Calculate the average daily streak based on local calendar days in the user's timezone.

    Args:
        completed_dates (list of datetime): A list of UTC datetime objects representing habit completion dates.
        user_tz (pytz.timezone): User's timezone.

    Returns:
        float: The average length of daily streaks in the user's timezone, based on local calendar days.

    Example:
        _get_average_daily_streak([
            datetime(2025, 4, 1, 14, 0, tzinfo=pytz.UTC),
            datetime(2025, 4, 2, 16, 0, tzinfo=pytz.UTC),
            datetime(2025, 4, 5, 10, 0, tzinfo=pytz.UTC)
        ], pytz.timezone('America/New_York'))
        Returns: 1.5  # Average streak: 2 days from 2025-04-01 to 2025-04-02, 1 day on 2025-04-05.
    """
    if not completed_dates:
        return 0

    # Convert all to local calendar dates and remove duplicates
    local_dates = sorted(set(dt.astimezone(user_tz).date() for dt in completed_dates))

    streaks = []
    current_streak = 1

    for i in range(1, len(local_dates)):
        if (local_dates[i] - local_dates[i - 1]).days == 1:
            current_streak += 1
        else:
            streaks.append(current_streak)
            current_streak = 1
    streaks.append(current_streak)

    return sum(streaks) / len(streaks)


def _get_average_weekly_streak(completed_dates, user_tz):
    """
    Calculate the average weekly streak based on local calendar weeks in the user's timezone.

    Args:
        completed_dates (list of datetime): A list of UTC datetime objects representing habit completion dates.
        user_tz (pytz.timezone): User's timezone.

    Returns:
        float: The average length of weekly streaks in the user's timezone, based on local calendar weeks.

    Example:
        _get_average_weekly_streak([
            datetime(2025, 4, 1, 14, 0, tzinfo=pytz.UTC),
            datetime(2025, 4, 8, 10, 0, tzinfo=pytz.UTC),
            datetime(2025, 4, 15, 9, 0, tzinfo=pytz.UTC)
        ], pytz.timezone('America/New_York'))
        Returns: 1.5  # Average streak: 2 weeks from 2025-03-30 to 2025-04-05, 1 week on 2025-04-12.
    """
    if not completed_dates:
        return 0

    # Convert to local calendar weeks and remove duplicates
    local_weeks = sorted(set(dt.astimezone(user_tz).isocalendar()[:2] for dt in completed_dates))

    streaks = []
    current_streak = 1

    for i in range(1, len(local_weeks)):
        prev_year, prev_week = local_weeks[i - 1]
        curr_year, curr_week = local_weeks[i]

        if (curr_year == prev_year and curr_week - prev_week == 1) or \
           (curr_year - prev_year == 1 and prev_week == 52 and curr_week == 1):
            current_streak += 1
        else:
            streaks.append(current_streak)
            current_streak = 1
    streaks.append(current_streak)

    return sum(streaks) / len(streaks)



@database_error_handler
def get_streak(habit_id, tz = pytz.timezone('UTC')):
    """
    Retrieve the streak details (longest and current) for a specific habit, based on calendar days or weeks
    in the user's timezone.

    Args:
        habit_id (int): The ID of the habit to retrieve streak data for.
        tz (pytz.timezone, optional): The timezone to convert completion dates to. Defaults to UTC.

    Returns:
        dict: A dictionary containing streak information, including the longest and current streaks.
            {
                "streak": int,  # The longest streak
                "table": [
                    {
                        "habit_id": int,  # Habit ID
                        "habit_name": str,  # Habit Name
                        "longest_streak": int,  # Longest Streak
                        "current_streak": int  # Current Streak
                    }
                ]
            }

    Example:
        get_streak(1)
        Returns: {
            "streak": 5,  # Longest streak of 5 days
            "table": [
                {
                    "habit_id": 1,
                    "habit_name": "Exercise",
                    "longest_streak": 5,
                    "current_streak": 3
                }
            ]
        }

    :param habit_id: The ID of the habit to retrieve streak details for.
    :param tz: The timezone to use for date comparisons (default is UTC).
    """
    habit = _get_habit_by_id(habit_id)
    if habit is None:
        return {"error": "Habit not found"}

    completed_dates = sorted([
        convert_iso_to_date(activity.completed_at)
        for activity in Activity.select(Activity.completed_at)
        .where(Activity.habit == habit_id)
        .order_by(Activity.completed_at)
    ])

    if not completed_dates:
        return {"streak": 0, "table": [habit.id, habit.name, habit.frequency, habit.created_at, 0, 0]}

    longest_streak = (
        _get_longest_daily_streak(completed_dates, tz)
        if habit.frequency == "DAILY"
        else _get_longest_weekly_streak(completed_dates, tz)
    )

    current_streak = (
        _get_current_daily_streak(completed_dates, tz)
        if habit.frequency == "DAILY"
        else _get_current_weekly_streak(completed_dates, tz)
    )

    return {
        "streak": longest_streak,
        "table": [[habit.id, habit.name, habit.frequency, habit.created_at, current_streak, longest_streak]],
    }


# @database_error_handler
# def _get_all_streaks(habits, tz = pytz.timezone('UTC')):
#     """
#     Retrieve streak data for all habits, including their longest and current streaks, based on local calendar days or weeks
#     in the user's timezone.
#
#     This function calculates the longest and current streak for each habit based on its
#     completion dates. It works for both daily and weekly habits.
#
#     Args:
#         tz (pytz.timezone, optional): The timezone to convert completion dates to. Defaults to UTC.
#
#     Returns:
#         dict: A dictionary containing a table with streak data for each habit. The table
#               includes habit ID, name, frequency, creation date, current streak, and longest streak.
#               {
#                   "table": [
#                       [habit_id, habit_name, frequency, created_at, current_streak, longest_streak],
#                   ]
#               }
#
#     Example:
#         get_all_streaks()
#         Returns:
#         {
#             "table": [
#                 [1, "Exercise", "DAILY", "01.01.2021", 5, 10],
#                 [2, "Reading", "WEEKLY", "15.03.2021", 3, 7]
#             ]
#         }
#     """
#     # habits = Habit.select(
#     #     Habit.id,
#     #     Habit.name,
#     #     Habit.frequency,
#     #     fn.strftime('%d.%m.%Y', Habit.created_at).alias("created_at"),
#     #     fn.strftime('%d.%m.%Y', Habit.last_completed_at).alias("last_completed_at"),
#     # )
#
#     streaks = []
#     for habit in habits:
#         completed_dates = sorted([
#             convert_iso_to_date(activity.completed_at)
#             for activity in Activity.select(Activity.completed_at)
#             .where(Activity.habit == habit.id)
#             .order_by(Activity.completed_at)
#         ])
#
#         if not completed_dates:
#             streaks.append([habit.id, habit.name, habit.frequency, habit.created_at, 0, 0])
#             continue
#
#         longest_streak = (
#             _get_longest_daily_streak(completed_dates, tz)
#             if habit.frequency == "DAILY"
#             else _get_longest_weekly_streak(completed_dates, tz)
#         )
#         current_streak = (
#             _get_current_daily_streak(completed_dates, tz)
#             if habit.frequency == "DAILY"
#             else _get_current_weekly_streak(completed_dates, tz)
#         )
#
#         streaks.append([habit.id, habit.name, habit.frequency, habit.created_at, current_streak, longest_streak])
#
#     return {
#         "table": streaks
#     }

@database_error_handler
def _get_all_streaks(habits, tz=pytz.timezone('UTC')):
    """
    Takes a list of habit model instances and returns their streaks (current & longest) in table form.
    """
    streak_table = []

    for habit in habits:
        completed_dates = sorted([
            convert_iso_to_date(activity.completed_at)
            for activity in Activity.select(Activity.completed_at)
            .where(Activity.habit == habit.id)
            .order_by(Activity.completed_at)
        ])

        if not completed_dates:
            current_streak = 0
            longest_streak = 0
        else:
            longest_streak = (
                _get_longest_daily_streak(completed_dates, tz)
                if habit.frequency == "DAILY"
                else _get_longest_weekly_streak(completed_dates, tz)
            )
            current_streak = (
                _get_current_daily_streak(completed_dates, tz)
                if habit.frequency == "DAILY"
                else _get_current_weekly_streak(completed_dates, tz)
            )

        streak_table.append([
            habit.id, habit.name, habit.description, habit.frequency,
            habit.created_at, habit.last_completed_at, current_streak, longest_streak
        ])

    return streak_table

@database_error_handler
def list_habits(frequency=None, created_at=None, completed_at=None, tz : pytz.tzinfo = pytz.timezone('UTC'), get_streaks=False):
    """
    List all habits with optional filters based on frequency, creation date, or last completion date, considering timezone.

    This function allows filtering habits based on their frequency ("DAILY" or "WEEKLY"), their creation date,
    or their last completion date. All dates are adjusted to the user’s specified timezone.

    Args:
        frequency (str, optional): The frequency of the habit, either "DAILY" or "WEEKLY".
        created_at (str, optional): The creation date of the habit in 'dd-mm-yyyy' format.
        completed_at (str, optional): The last completion date of the habit in 'dd-mm-yyyy' format.
        timezone (pytz.timezone, optional): The timezone to convert dates to. Defaults to UTC.
        get_streak (bool, Optional): Flag to initiate streak calculation. Defaults to False.

    Returns:
        dict: A dictionary containing the habit details after applying the filters.
        {
            "table": [[habit_id, habit_name, habit_description, habit_frequency, created_at, updated_at]]
        }

    Example:
        list_habits(frequency="DAILY", created_at="01-01-2021")
        Returns:
        {
            "table": [
                [1, "Exercise", "Daily workout", "DAILY", "01.01.2021", "05.01.2021"],
                [2, "Reading", "Read a book daily", "DAILY", "01.01.2021", "06.01.2021"]
            ]
        }

    :param frequency: The frequency of the habit ("DAILY" or "WEEKLY").
    :param created_at: The creation date to filter by, in 'dd-mm-yyyy' format.
    :param completed_at: The completion date to filter by, in 'dd-mm-yyyy' format.
    :param tz: The timezone to use for converting dates (default is UTC).
    :param get_streaks:  Flag to initiate streak calculation. Defaults to False.
    """
    all_habits = Habit.select(
        Habit.id,
        Habit.name,
        Habit.description,
        Habit.frequency,
        Habit.created_at,
        Habit.last_completed_at,
    )

    if frequency and frequency.upper() in ["DAILY", "WEEKLY"]:
        all_habits = all_habits.where(Habit.frequency == frequency.upper())
    elif frequency and frequency.upper() not in ["DAILY", "WEEKLY"]:
        return {"error": "ERROR: Invalid frequency"}

    if created_at:
        created_at = date_str_to_utc_iso(created_at, tz).split(" ")[0]
        all_habits = all_habits.where(fn.DATE(Habit.created_at) == created_at)

    if completed_at:
        completed_at = date_str_to_utc_iso(completed_at, tz).split(" ")[0]
        all_habits = all_habits.join(Activity).where(fn.DATE(Activity.completed_at) == completed_at)

    habits = [[h.id, h.name, h.description, h.frequency, h.created_at, h.last_completed_at] for h in all_habits]

    # Optional if Streaks are added
    if get_streaks:
        habits = _get_all_streaks(all_habits, tz)

    return {
        "table": habits
    }


@database_error_handler
def get_most_consistent_habit(tz = pytz.timezone('UTC')):
    """
    Get the habit with the highest average streak, based on the habit's frequency (DAILY or WEEKLY),
    considering the user's timezone.

    This function calculates the average streak for each habit (both daily and weekly) and returns
    the habit with the highest average streak along with the corresponding average streak value.

    Args:
        tz (pytz.timezone, optional): The timezone to convert completion dates to. Defaults to UTC.

    Returns:
        dict: A dictionary containing the name of the most consistent habit and the highest average streak.
            {
                "most_consistent": str,  # Habit name with the highest average streak
                "average_streak": float  # The average streak value
            }

    Example:
        get_most_consistent_habit()
        Returns:
        {
            "most_consistent": "Exercise",
            "average_streak": 4.5
        }

    :param tz: The timezone to use for calculating streaks (default is UTC).
    """
    habits = Habit.select().join(Activity).group_by(Habit.id)

    most_consistent = None
    highest_avg_streak = 0

    for habit in habits:
        completed_dates = [
            # activity.completed_at.date()
            convert_iso_to_date(activity.completed_at)
            for activity in Activity.select(Activity.completed_at)
            .where(Activity.habit == habit.id)
            .order_by(Activity.completed_at)
        ]

        if habit.frequency == "DAILY":
            avg_streak = _get_average_daily_streak(completed_dates, tz)
        else:
            avg_streak = _get_average_weekly_streak(completed_dates, tz)

        if avg_streak > highest_avg_streak:
            highest_avg_streak = avg_streak
            most_consistent = habit

    return {
        "most_consistent": most_consistent.name if most_consistent else "None",
        "average_streak": highest_avg_streak
    }


@database_error_handler
def get_least_consistent_habit(tz = pytz.timezone('UTC')):
    """
    Get the habit with the lowest average streak, based on the habit's frequency (DAILY or WEEKLY),
    considering the user's timezone.

    This function calculates the average streak for each habit (both daily and weekly) and returns
    the habit with the lowest average streak along with the corresponding average streak value.

    Args:
        tz (pytz.timezone, optional): The timezone to convert completion dates to. Defaults to UTC.

    Returns:
        dict: A dictionary containing the name of the least consistent habit and the lowest average streak.
            {
                "least_consistent": str,  # Habit name with the lowest average streak
                "average_streak": float  # The average streak value
            }

    Example:
        get_least_consistent_habit()
        Returns:
        {
            "least_consistent": "Reading",
            "average_streak": 1.2
        }

    :param tz: The timezone to use for calculating streaks (default is UTC).
    """
    habits = Habit.select().join(Activity).group_by(Habit.id)

    least_consistent = None
    lowest_avg_streak = float("inf")

    for habit in habits:
        completed_dates = [
            # activity.completed_at.date()
            convert_iso_to_date(activity.completed_at)
            for activity in Activity.select(Activity.completed_at)
            .where(Activity.habit == habit.id)
            .order_by(Activity.completed_at)
        ]

        if habit.frequency == "DAILY":
            avg_streak = _get_average_daily_streak(completed_dates, tz)
        else:
            avg_streak = _get_average_weekly_streak(completed_dates, tz)

        if avg_streak < lowest_avg_streak:
            lowest_avg_streak = avg_streak
            least_consistent = habit

    return {
        "least_consistent": least_consistent.name if least_consistent else "None",
        "average_streak": lowest_avg_streak
    }


@database_error_handler
def get_consistency(tz = pytz.timezone('UTC')):
    """
    Get a summary of the most and least consistent habits based on average streaks.

    This function fetches the most and least consistent habits and formats them into a
    single dictionary with a clean, human-readable table format.

    Args:
        tz (pytz.timezone, optional): Timezone to use for streak calculations. Defaults to UTC.

    Returns:
        dict: A dictionary with a single key "table" containing a formatted string,
              or {"error": "Could not retrieve consistency data"} if something fails.

        Example:
        {
            "table": "Most Consistent: Read 10 Pages, Avg Streak: 6.8  |  Least Consistent: Amazing Habit, Avg Streak: 1.0"
        }
    """
    most = get_most_consistent_habit(tz)
    least = get_least_consistent_habit(tz)

    if not most or not least:
        return {"error": "Could not retrieve consistency data"}

    table = [
        ["Most Consistent", most["most_consistent"],  "Average Streak",most["average_streak"]],
        ["Least Consistent", least["least_consistent"], "Average Streak", least["average_streak"]],
    ]

    return {"table": table}
