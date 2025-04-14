"""
Module containing utility functions and decorators for handling database operations,
timezone-aware datetime parsing, formatting, and conversion in the habit tracking application.

This module provides:
- A decorator for handling database-related errors consistently (`database_error_handler`).
- Helper functions for manipulating and converting dates and times:
    - `format_date_to_string(dt)`: Converts a datetime object to 'dd.mm.yyyy' string format.
    - `get_current_utc_time()`: Returns the current time in UTC.
    - `parse_iso_datetime(date_str)`: Parses an ISO 8601 formatted datetime string into a datetime object.
    - `convert_user_date_str_to_iso(date)`: Converts a user-provided 'dd/mm/yyyy' string to ISO format.
    - `parse_user_date_str_to_datetime(date_str)`: Parses a user 'dd/mm/yyyy' string to a datetime object.
    - `format_datetime_for_user(dt, timezone)`: Converts and formats a UTC datetime to the user's timezone.
    - `convert_iso_to_date(iso_str)`: Converts an ISO 8601 string or datetime to a UTC-aware datetime object.
    - `date_str_to_utc_iso(date_str, tz)`: Converts a day-first date string in user timezone to ISO UTC string.
    - `is_valid_timezone(tz)`: Checks if a timezone string is valid using pytz.

These functions ensure consistency in date handling, help maintain correct timezone conversions,
and provide robust error handling throughout the habit tracking application.
"""


import pytz
from pytz.tzinfo import BaseTzInfo
from peewee import DatabaseError, IntegrityError
from dateutil import parser
from datetime import datetime


def database_error_handler(func):
    """
    A decorator to handle common database-related errors such as DatabaseError,
    IntegrityError, and ValueError. If any of these errors occur, it returns
    an error message in a consistent format.

    Args:
        func (function): The function to wrap and apply error handling.

    Returns:
        wrapper (function): A wrapped function that catches and handles database errors.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (DatabaseError, IntegrityError, ValueError) as e:
            return {"error": str(e), "table": None}
        except Exception as e:
            return {"error": f"Unknown error occurred: {e}", "table": None}
    return wrapper


def format_date_to_string(dt):
    """
    Converts a given datetime object to a string in 'dd.mm.yyyy' format.

    Args:
        dt (datetime): The datetime object to format.

    Returns:
        str: The formatted date as a string, or None if the datetime is None.

    Example:
        format_date_to_string(datetime(2021, 10, 15))
        Returns: '15.10.2021'
    """
    return dt.strftime('%d.%m.%Y') if dt else None


def get_current_utc_time():
    """
    Returns the current time in UTC timezone.

    Returns:
        datetime: The current UTC time.
    """
    return datetime.now(pytz.UTC)


def parse_iso_datetime(date_str):
    """
    Parses a datetime string in ISO format (e.g., '2021-10-15T13:45:00') into a
    Python datetime object.

    Args:
        date_str (str): The ISO-format datetime string to parse.

    Returns:
        datetime: The parsed datetime object.

    Example:
        parse_iso_datetime('2021-10-15T13:45:00')
        Returns: datetime.datetime(2021, 10, 15, 13, 45)
    """
    return parser.parse(date_str)


def convert_user_date_str_to_iso(date):
    """
    Converts a date string provided by the user in day-first format
    (e.g., '15/10/2021') into an ISO format string ('YYYY-MM-DD').

    Args:
        date (str): The date string in day-first format (e.g., '15/10/2021').

    Returns:
        str: The converted date string in ISO format (e.g., '2021-10-15').

    Example:
        convert_user_date_str_to_iso('15/10/2021')
        Returns: '2021-10-15'
    """
    return parser.parse(date, dayfirst=True).strftime("%Y-%m-%d")

def date_str_to_utc_iso(date_str: str, tz: pytz.tzinfo = pytz.timezone('UTC')) -> str:
    dt_naive = parser.parse(date_str, dayfirst=True)
    dt_local = tz.localize(dt_naive)
    dt_utc = dt_local.astimezone(pytz.UTC)
    return dt_utc.strftime("%Y-%m-%d %H:%M:%S%z")[:-2] + ":" + dt_utc.strftime("%z")[-2:]


def parse_user_date_str_to_datetime(date_str):
    """
    Parses a user-provided date string in day-first format (e.g., '15/10/2021')
    into a Python datetime object.

    Args:
        date_str (str): The date string in day-first format (e.g., '15/10/2021').

    Returns:
        datetime: The parsed datetime object.

    Example:
        parse_user_date_str_to_datetime('15/10/2021')
        Returns: datetime.datetime(2021, 10, 15, 0, 0)
    """
    return parser.parse(date_str, dayfirst=True)


def format_datetime_for_user(dt: datetime, timezone: str, fmt="%d.%m.%Y") -> str:
    """
    Converts a UTC datetime object to user's timezone and formats it.

    Args:
        dt (datetime): UTC datetime object
        timezone (str, optional): User timezone (e.g., 'Asia/Kolkata')
        fmt (str): Format string to return (default: '%d.%m.%Y')

    Returns:
        str: Formatted datetime string in user timezone
    """
    user_tz = pytz.timezone(timezone)
    return dt.astimezone(user_tz).strftime(fmt)


def convert_iso_to_date(iso_str):
    """
    Convert an ISO 8601 string or datetime object to a timezone-aware datetime object in UTC.

    Args:
        iso_str (str | datetime): The ISO 8601 string or a datetime object.

    Returns:
        datetime: A timezone-aware datetime object in UTC.
    """
    if isinstance(iso_str, str):
        dt = datetime.fromisoformat(iso_str)
    else:
        dt = iso_str

    # Make sure it's timezone-aware
    if dt.tzinfo:
        return dt
    return pytz.UTC.localize(dt)


def is_valid_timezone(tz: str | BaseTzInfo) -> bool:
    """
    Check if a given timezone string or pytz timezone object is valid.

    Args:
        tz (str | pytz.tzinfo.BaseTzInfo): The timezone to validate, either as a string name
        (e.g., "Asia/Kolkata") or as a pytz timezone object.

    Returns:
        bool: True if the timezone is valid, False otherwise.

    Examples:
        is_valid_timezone("UTC")                      # Returns: True
        is_valid_timezone(pytz.timezone("UTC"))       # Returns: True
        is_valid_timezone("Mars/Phobos")              # Returns: False
    """
    if isinstance(tz, BaseTzInfo):
        return tz.zone in pytz.all_timezones
    elif isinstance(tz, str):
        return tz in pytz.all_timezones
    return False
