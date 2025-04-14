"""
This module provides service functions to manage user-specific settings:
- Display timezone
- Username
- Preferred color

NOTE:
This application is designed for a single user only.
Hence, the `Config` model is expected to contain only one row,
which is created at application setup and updated as needed.
"""

from habit_tracker.models import Config
from habit_tracker.utils import database_error_handler, get_current_utc_time, is_valid_timezone


@database_error_handler
def get_display_timezone():
    """
    Retrieve the current display timezone from the Config.

    Returns:
        dict: A dictionary with the current display timezone.
              Example: {"timezone": "Asia/Kolkata"}
    """
    config = Config.get()
    return {"timezone": config.timezone}


@database_error_handler
def set_display_timezone(timezone: str):
    """
    Update the display timezone in the Config.

    Args:
        timezone (str): The new timezone to set.

    Returns:
        dict: A success message indicating the new timezone.
              Example: {"success": "Timezone updated to 'Asia/Kolkata'"}
    """
    config = Config.get()

    # Make sure only valid timezone is stored
    if not is_valid_timezone(timezone):
        timezone = "UTC"

    config.timezone = timezone
    config.updated_at = get_current_utc_time()
    config.save()
    return {"success": f"Timezone updated to '{timezone}'"}


@database_error_handler
def get_username():
    """
    Retrieve the current username from the Config.

    Returns:
        dict: A dictionary with the current username.
              Example: {"username": "john_doe"}
    """
    config = Config.get()
    return {"username": config.username}


@database_error_handler
def set_username(new_username: str):
    """
    Update the username in the Config.

    Args:
        new_username (str): The new username to set.

    Returns:
        dict: A success message indicating the updated username.
              Example: {"success": "Username updated to 'john_doe'"}
    """
    config = Config.get()
    config.username = new_username
    config.updated_at = get_current_utc_time()
    config.save()
    return {"success": f"Username updated to '{new_username}'"}


@database_error_handler
def get_user_color():
    """
    Retrieve the user's preferred color from the Config.

    Returns:
        dict: A dictionary with the current color code.
              Example: {"color": "#ffcc00"}
    """
    config = Config.get()
    return {"color": config.color}


@database_error_handler
def set_user_color(color_code: str):
    """
    Update the user's preferred color in the Config.

    Args:
        color_code (str): The new hex color code to set.
                          Example: "#00ffcc"

    Returns:
        dict: A success message indicating the new color.
              Example: {"success": "Color updated to '#00ffcc'"}
    """
    config = Config.get()
    config.color = color_code
    config.updated_at = get_current_utc_time()
    config.save()
    return {"success": f"Color updated to '{color_code}'"}


@database_error_handler
def get_user_config():
    """
    Retrieve all user configuration settings at once.

    Returns:
        dict: A dictionary with the username, timezone, and preferred color.
              Example: {
                  "username": "john_doe",
                  "timezone": "Asia/Kolkata",
                  "color": "#00ffcc"
              }
    """
    config = Config.get()
    return {
        "username": config.username,
        "timezone": config.timezone,
        "color": config.color
    }


@database_error_handler
def set_user_config(username: str = None, timezone: str = None, color: str = None):
    """
    Update one or more user configuration settings at once.

    Only the provided parameters will be updated.

    Args:
        username (str, optional): The new username to set.
        timezone (str, optional): The new timezone to set.
        color (str, optional): The new color hex code to set.

    Returns:
        dict: A dictionary showing which fields were updated.
              Example: {
                  "success": {
                      "username": "john_doe",
                      "color": "#00ffcc"
                  }
              }
    """
    config = Config.get()
    updates = {}

    if not is_valid_timezone(timezone):
        timezone = None

    if username:
        config.username = username
        updates["username"] = username
    if timezone:
        config.timezone = timezone
        updates["timezone"] = timezone
    if color:
        config.color = color
        updates["color"] = color

    if updates:
        config.updated_at = get_current_utc_time()
        config.save()
        return {"success": updates}
    else:
        return {"warning": "No fields were updated because no values were provided."}