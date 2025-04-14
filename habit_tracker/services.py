"""
Module for managing habits in the habit tracking application. This module includes
functions to add, edit, delete habits, as well as marking them as completed or
unmarking them. It also provides a function for retrieving active habits by a
specific date. All functions in this module are decorated with a database error
handler to ensure consistent error handling and data integrity.

This module provides:
- Functions for adding, editing, and deleting habits.
- Functions for marking habits as completed or unmarking them.
- A function for retrieving active habits by a specific date.
- Error handling using a database error handler for all database interactions.

Each function interacts with the `Habit` and `Activity` models from the
`habit_tracker.models` module, allowing for effective habit tracking and activity management.

Functions:
    get_habit(): Retrieve a specific habit based on its ID.
    edit_habit(): Edit the details of an existing habit.
    add_habit(): Add a new habit to the system.
    mark_completed(): Mark a habit as completed on a specific date.
    unmark_completed(): Unmark a habit completion on a specific date.
    delete_habit(): Delete a habit from the system.
    get_active_habits_by_date(): Retrieve all active habits that should be completed by a specific date.
"""

from peewee import fn
from datetime import timedelta
from habit_tracker.utils import database_error_handler, get_current_utc_time, parse_user_date_str_to_datetime, \
    convert_iso_to_date
from habit_tracker.models import Habit, Activity

@database_error_handler
def get_habit(habit_id):
    """
    Retrieve a habit from the database by its ID.

    Args:
        habit_id (int): The ID of the habit to retrieve.

    Returns:
        dict: A dictionary containing the habit details or an error message if not found.
        {
            "table": [[habit_id, habit_name, habit_description, habit_frequency, created_at, last_completed_at]],
            "error": "Error message" (if the habit is not found or another error occurs)
        }

    Example:
        get_habit(1)
        Returns: {
            "table": [[1, "Exercise", "Morning workout", "DAILY", "01.01.2021", "01.01.2021"]],
        }
    """
    habit = Habit.get_or_none(Habit.id == habit_id)
    return {"table": [[habit.id, habit.name, habit.description, habit.frequency, habit.created_at, habit.last_completed_at]]} if habit else None


@database_error_handler
def add_habit(name, description, frequency):
    """
    Add a new habit to the database.

    Args:
        name (str): The name of the habit.
        description (str): The description of the habit.
        frequency (str): The frequency of the habit ('DAILY' or 'WEEKLY').

    Returns:
        dict: A dictionary containing the habit details after creation.
        {
            "table": [[habit_id, habit_name, habit_description, habit_frequency, created_at, updated_at]]
        }

    Example:
        add_habit("Exercise", "Morning workout", "DAILY")
        Returns: {
            "table": [[1, "Exercise", "Morning workout", "DAILY", "01.01.2021", "01.01.2021"]]
        }
    """
    today = get_current_utc_time()
    habit = Habit.create(
        name=name, description=description, frequency=frequency,
        created_at=today, updated_at=today
    )
    return {
        # "table": [[habit.id, habit.name, habit.description, habit.frequency,
        #            format_date_to_string(habit.created_at), format_date_to_string(habit.created_at)]]

        # "table": [[habit.id, habit.name, habit.description, habit.frequency,
        #            habit.created_at, habit.created_at]]

        "table": [[habit.id, habit.name, habit.description, habit.frequency,
                   habit.created_at, habit.last_completed_at]]
    }


@database_error_handler
def mark_completed(habit_id: int):
    """
    Mark a habit as completed for today.

    Args:
        habit_id (int): The ID of the habit to mark as completed.

    Returns:
        dict: A success message or an error message if the habit is already marked as completed today or does not exist.

    Example:
        mark_completed(1)
        Returns: {
            "success": "Habit 'Exercise' marked as completed on 01.01.2021."
        }
    """
    today = get_current_utc_time()
    habit = Habit.get_or_none(Habit.id == habit_id)

    if not habit:
        return {"error": f"Habit with ID: {habit_id} does not exist"}
    if habit.last_completed_at and convert_iso_to_date(habit.last_completed_at).date() == today.date():
        return {"error": f"Habit {habit_id} is already marked completed for today"}

    habit.last_completed_at = today
    habit.save()
    Activity.create(habit=habit, completed_at=today)

    return {"success": f"Habit '{habit.name}' marked as completed on {today.date().strftime('%d.%m.%Y')}."}


@database_error_handler
def unmark_completed(habit_id: int):
    """
    Unmark a habit as completed for today.

    Args:
        habit_id (int): The ID of the habit to unmark.

    Returns:
        dict: A success message or an error message if no completion record exists for today.

    Example:
        unmark_completed(1)
        Returns: {
            "success": "Habit 'Exercise' no longer marked as completed on 01.01.2021."
        }
    """
    today = get_current_utc_time()
    habit = Habit.get_or_none(Habit.id == habit_id)

    if not habit:
        return {"error": f"Habit with ID: {habit_id} does not exist"}
    if not habit.last_completed_at:
        return {"error": f"Habit with ID: {habit_id} is never been completed"}
    if convert_iso_to_date(habit.last_completed_at).date() != today.date():
        return {"error": f"Habit with ID: {habit_id} was not completed on today"}

    activities = Activity.select().where(Activity.habit == habit).order_by(Activity.completed_at.desc())
    today_activity = activities.where(fn.DATE(Activity.completed_at) == today.date()).first()

    if not today_activity:
        return {"error": "No completion record found for today in activities."}

    # Find the last completion that isn't today
    previous_activity = activities.where(fn.DATE(Activity.completed_at) != today.date()).first()
    habit.last_completed_at = previous_activity.completed_at if previous_activity else None
    habit.save()

    today_activity.delete_instance()

    return {"success": f"Habit '{habit.name}' no longer marked as completed on {today.date().strftime('%d.%m.%Y')}."}


@database_error_handler
def delete_habit(habit_id: int):
    """
    Delete a habit from the database.

    Args:
        habit_id (int): The ID of the habit to delete.

    Returns:
        dict: A success message or an error message if the habit does not exist.

    Example:
        delete_habit(1)
        Returns: {
            "success": "Habit 'Exercise' has been deleted."
        }
    """
    habit = Habit.get_or_none(Habit.id == habit_id)
    if habit:
        habit.delete_instance()
        return {"success": f"Habit '{habit.name}' has been deleted."}
    return {"error": f"Habit with ID: {habit_id} does not exist", "table": None}


@database_error_handler
def edit_habit(habit_id: int, name: str, description: str):
    """
    Edit an existing habit's name and/or description.

    Args:
        habit_id (int): The ID of the habit to edit.
        name (str): The new name of the habit.
        description (str): The new description of the habit.

    Returns:
        dict: The updated habit details.

    Example:
        edit_habit(1, "New Exercise", "New morning workout description")
        Returns: {
            "table": [[1, "New Exercise", "New morning workout description", "DAILY", "01.01.2021", "01.01.2021"]]
        }
    """
    today = get_current_utc_time()
    habit = Habit.get_or_none(Habit.id == habit_id)
    if not habit:
        return {"error": f"Habit {habit_id} does not exist"}

    habit.name = name or habit.name
    habit.description = description or habit.description
    habit.updated_at = today
    habit.save()

    return {"table": [[habit.id, habit.name, habit.description, habit.frequency, habit.created_at, habit.last_completed_at]]} if habit else None

    # return {
    #     "table": [[habit.id, habit.name, habit.description, habit.frequency,
    #                format_date_to_string(habit.created_at), today.strftime('%d.%m.%Y')]]
    # }


@database_error_handler
def get_active_habits_by_date(date_str: str):
    """
    Retrieve active habits for a given date, considering the frequency (daily or weekly).

    Args:
        date_str (str): The date string in 'dd.mm.yyyy' format to retrieve active habits for.

    Returns:
        dict: A dictionary containing active habits or an error message if no active habits are found.

    Example:
        get_active_habits_by_date('01.01.2021')
        Returns: {
            "table": [[1, "Exercise", "Morning workout", "DAILY", "01.01.2021", "01.01.2021"]],
        }
    """
    user_date = parse_user_date_str_to_datetime(date_str)
    seven_days_ago = user_date - timedelta(days=7)

    query = Habit.select(
        Habit.id,
        Habit.name,
        Habit.description,
        Habit.frequency,
        fn.strftime('%d-%m-%Y', Habit.created_at).alias("created_at"),
        fn.strftime('%d-%m-%Y', Activity.completed_at).alias("completed_at")
    ).join(Activity).where(
        (Habit.frequency == 'DAILY') & (fn.DATE(Activity.completed_at) == user_date.date()) |
        (Habit.frequency == 'WEEKLY') & (
            fn.DATE(Activity.completed_at).between(seven_days_ago.date(), user_date.date()))
    ).distinct()

    result = [
        [h.id, h.name, h.description, h.frequency, h.created_at, h.completed_at]
        for h in query
    ]

    return {"table": [result]} if len(result) > 0 else None
