"""
HabitX CLI Interface
====================

This module provides a command-line interface (CLI) for interacting with the HabitX habit tracking application.
It enables users to manage habits, view analytics, and configure personal settings through a terminal-based
text user interface (TUI).

Features:
---------
- Add, edit, delete, and complete habits.
- View streaks, consistency, and other habit performance metrics.
- Configure and persist user preferences such as timezone, username, and terminal color.
- Interactive menu system with keyboard navigation.
- Supports both interactive prompts and command-line arguments via the Fire library.

Dependencies:
-------------
- fire          : For dynamic CLI command dispatching.
- pyfiglet      : For rendering the HabitX ASCII logo.
- pytz          : For robust timezone handling.
- tabulate      : For pretty-printing tables.
- rich.console  : For colored and styled terminal output.
- rich.prompt   : For interactive text prompts.

Modules:
--------
- analytics     : Provides analytical functions like streaks and consistency.
- services      : Contains core habit CRUD and state-management logic.
- user          : Manages user configuration and persistence.
- utils         : Helper functions for timezone validation and date conversions.

Usage:
------
Run without arguments to launch the interactive menu:
    $ python cli.py

Or use direct commands for automation or scripting:
    $ python cli.py add --n="Exercise" --d="Morning workout" --f="daily"
"""


import datetime
import sys
import fire
import pyfiglet
import pytz
import tabulate
from rich.console import Console
from rich.prompt import Prompt
from habit_tracker import analytics, services, user
from habit_tracker.utils import is_valid_timezone, convert_iso_to_date


class CLI:
    """
    Command Line Interface for the Habit Tracker application.

    This class provides an interactive or command-line driven interface for managing user habits.
    It uses the `fire` library for command-line argument parsing and the `rich` library for enhanced console output.

    Attributes:
        console (Console): Rich console for styled output.
        prompt (Prompt): Rich prompt for user input.
        timezone (pytz.timezone): The user's configured timezone, default is UTC.
        terminal_color (str): Color used for styled console output, default is "blue".
        username (str): Username of the configured user, default is "user".
    """


    def __init__(self):
        """
         Initialize the CLI instance.

         Loads user configuration including timezone, terminal color, and username from the config store.
         Initializes rich console and prompt for interaction.
         """
        self.console = Console()
        self.prompt = Prompt()
        self.timezone = pytz.timezone('UTC')
        self.terminal_color ="blue"
        self.username = "user"
        self._get_config()


    def _get_config(self):
        """
         Load user configuration from persistent storage.

         Updates the instance's timezone, terminal color, and username based on the stored user preferences.
         """
        user_config = user.get_user_config()
        self.timezone = pytz.timezone(user_config['timezone'])
        self.terminal_color = user_config['color']
        self.username = user_config['username']


    def fire(self):
        """
        Start the Fire CLI interface.

        This enables the command-line interaction with CLI methods directly using the `fire` library.
        Typically called when executing the script directly to expose CLI commands.
        """
        fire.Fire(self)


    def _console_print(self, message):
        """
        Print a styled message to the console using the user's configured terminal color.

        Args:
            message (str): The message to display.
        """
        self.console.print(f"[bold {self.terminal_color}]{message}[/bold {self.terminal_color}]")


    def _console_prompt(self, message):
        """
         Prompt the user for input with styled text using the user's terminal color.

         Handles keyboard interrupts gracefully and exits the program if interrupted.

         Args:
             message (str): The prompt message to display.

         Returns:
             str: The user input from the console.
         """
        try:
            return self.prompt.ask(f"[bold {self.terminal_color}]{message}[/bold {self.terminal_color}]")
        except KeyboardInterrupt:
            self._console_print("[red]Input interrupted. Exiting...[/red]")
            sys.exit(0)


    def _console_error(self, message):
        """
        Print an error message to the console in bold red text.

        Args:
            message (str): The error message to display.
        """
        self.console.print(f"[bold red]{message}[/bold red]")


    def _format_datetime_to_date(self, table, indices):
        """
        Convert datetime objects in specified columns of a table to user-local date strings.

        Args:
            table (list[list[Any]]): A 2D list representing rows and columns of data.
            indices (list[int]): Indices of columns to format as date strings.

        Returns:
            list[list[Any]]: A new table with formatted date strings in specified columns.
        """
        tz = self.timezone
        return [
            [
                item.astimezone(tz).strftime("%d.%m.%Y") if isinstance(item, datetime.date) and i in indices else item
                for i, item in enumerate(row)
            ]
            for row in table
        ]


    def _format_iso_string_to_date(self, table, indices):
        """
        Convert ISO-formatted date strings in specified columns to user-local date strings.

        Args:
            table (list[list[Any]]): A 2D list representing rows and columns of data.
            indices (list[int]): Indices of columns to format as date strings.

        Returns:
            list[list[Any]]: A new table with formatted date strings in specified columns.
        """
        tz = self.timezone
        return [
            [
                convert_iso_to_date(item).astimezone(tz).strftime("%d.%m.%Y") if isinstance(item, str) and i in indices else item
                for i, item in enumerate(row)
            ]
            for row in table
        ]


    # Handle Repeated Pattern
    def _handle_result_error(self, msg, error):
        """
        Print a formatted error message to the console.

        Args:
            msg (str): The base error message to display.
            error (str or Exception or None): Additional error detail, if available.
        """
        self._console_error(f"{msg}. {error if error else ''}")


    def user(self, edit : bool = False, n = None, tz = None, c = None):
        """
        Display or edit the user's configuration including username, timezone, and terminal color.

        Args:
            edit (bool): If True, prompts the user to edit their configuration. Defaults to False.
            n (str, optional): New username. If None, prompts the user.
            tz (str, optional): New timezone. If None, prompts the user.
            c (str, optional): New terminal color. If None, prompts the user.

        Behavior:
            - If `edit` is False: Displays the current user configuration.
            - If `edit` is True and no arguments are provided: Prompts the user for values.
            - If arguments are provided: Uses them to update the config without prompting.

        Validation:
            - If the provided timezone is invalid, it will default to "UTC".
            - The terminal color input is converted to lowercase and stripped.

        Outputs:
            - Success or failure message is printed to the console using color formatting.
        """
        if edit is False:
            user_config = user.get_user_config()
            self._console_print(f"Username: {user_config['username']}, Timezone: {user_config['timezone']}, Color: {user_config['color']}")
            return

        if all(arg is None for arg in (n, tz, c)):
            self._console_print("Let's set up the user...")

            username_input = self._console_prompt(f"Please enter your username [Current: {self.username}]")
            username = username_input.strip() if username_input.strip() else self.username

            timezone_input = self._console_prompt(f"Please enter your timezone [Current: {self.timezone}]")
            timezone = timezone_input.strip() if timezone_input.strip() else self.timezone

            color_input = self._console_prompt(
                f"Please enter the color of your choice [Current: {self.terminal_color}]")
            color = color_input.strip().lower() if color_input.strip() else self.terminal_color.lower()

        else:
            username = n or self.username
            timezone = tz or self.timezone
            color = (c or self.terminal_color).strip().lower()

        if not is_valid_timezone(timezone):
            timezone = "UTC"
            self._console_error(f"Invalid timezone, reverting to UTC")

        user_success = user.set_user_config(username, timezone, color)
        if user_success["success"]:
            self._console_print("Successfully Updated")
            self._console_print(f"[{color}]Username: {username}, timezone: {timezone}, color: {color}[/{color}]")
        else:
            self._console_error("Failed to Update")


    def add(self, n = None, d = None, f = None):
        """
        Add a new habit with the specified name, description, and frequency.

        Args:
            n (str, optional): The name of the habit. If not provided, prompts the user.
            d (str, optional): The description of the habit. If not provided, prompts the user.
            f (str, optional): The frequency of the habit ("Daily" or "Weekly").
                              If not provided, prompts the user.

        Behavior:
            - Validates that frequency is either "DAILY" or "WEEKLY".
            - Adds the habit using the `services.add_habit` function.
            - Displays the added habit in a formatted table if successful.
            - Prints an error message if the habit could not be added.
        """
        name = (n or self._console_prompt("Please enter a habit name")).strip()
        desc = (d or self._console_prompt("Please enter a habit description")).strip()
        freq = (f or self._console_prompt("Please enter a habit frequency [Daily / Weekly]")).strip().upper()

        if freq not in ["DAILY", "WEEKLY"]:
            self._console_error("Invalid frequency, please choose from [DAILY, WEEKLY]")
            return

        results = services.add_habit(name= name, description= desc, frequency= freq)

        if results.get("table"):
            updated_table = self._format_datetime_to_date(results["table"], [4, 5])
            headers = ["ID", "Name", "Description", "Frequency", "Date", "Updated At"]
            tabulated_info = tabulate.tabulate(updated_table, headers = headers, tablefmt="pretty")
            self._console_print(tabulated_info)
        else:
            self._console_error(f"Sorry, No habits were added: {results.get('error')}.")
            return


    def delete(self, i = None):
        """
        Delete a habit by its ID.

        Args:
            i (int or str, optional): The ID of the habit to delete. If not provided, prompts the user.

        Behavior:
            - Calls `services.delete_habit` with the provided ID.
            - Prints confirmation if successful.
            - If deletion fails, displays an error message with details.
        """
        i = i or self._console_prompt("Please enter a habit id")
        results = services.delete_habit(i)
        if results.get("success"):
            self._console_print(f"Deleted habit: {results.get('success')}")
            return
        self._handle_result_error("Failed to Delete", results.get('error'))


    def mark(self, i = None):
        """
        Mark a habit as completed for today by its ID.

        Args:
            i (int or str, optional): The ID of the habit to mark. If not provided, prompts the user.

        Behavior:
            - Calls `services.mark_completed` with the given ID.
            - Prints confirmation message if successful.
            - Displays an error if the operation fails.
        """
        i = i or self._console_prompt("Please enter a habit id")
        results = services.mark_completed(i)
        if results.get("success"):
            self._console_print(f"Completed habit: {results.get('success')}")
            return
        self._handle_result_error("Failed to Mark as Completed", results.get('error'))


    def unmark(self, i = None):
        """
        Unmark a habit as completed for today by its ID.

        Args:
            i (int or str, optional): The ID of the habit to unmark. If not provided, prompts the user.

        Behavior:
            - Calls `services.unmark_completed` to reverse a mark.
            - Prints confirmation message if successful.
            - Displays an error if the operation fails.
        """
        i = i or self._console_prompt("Please enter a habit id")
        results = services.unmark_completed(i)
        if results.get("success"):
            self._console_print(f"Unmarked habit: {results.get('success')}")
            return
        self._handle_result_error("Failed to Mark as Uncompleted", results.get('error'))


    def edit(self, i : int = None, n = None, d = None):
        """
        Edit an existing habit's name and description. Frequency cannot be changed.

        Args:
            i (int, optional): The ID of the habit to edit. If not provided, prompts the user.
            n (str, optional): The new name of the habit. If not provided, prompts for it.
            d (str, optional): The new description of the habit. If not provided, prompts for it.

        Behavior:
            - Prompts for Habit ID if not provided.
            - Prompts for name and description if not passed via arguments.
            - Calls `services.edit_habit` to update the habit.
            - Displays the updated habit details in a table if successful.
            - Shows an error message on failure.
        """
        self._console_print("Please feel free to edit name and description. Frequency [red]CAN NOT[/red] be changed!")
        i = i or self._console_prompt("Please enter a habit id")
        if i is None:
            self._console_error("No Habit ID was provided.")
            return

        if all(arg is None for arg in (n, d)):
            self._console_print("Let's set up the habit...")
            name = n if n else self._console_prompt(
                "Please enter the Habit Name [Leave this Empty for No change]: ").strip() or None
            desc = d if d else self._console_prompt(
                "Please enter your description [Leave this Empty for No change]: ").strip() or None
        else:
            name = n.strip() or None
            desc = d.strip() or None

        results = services.edit_habit(i, name, desc)
        if results.get("table"):
            headers = ["ID", "Name", "Description", "Frequency", "Date", "Updated At"]
            tabulated_info = tabulate.tabulate(results.get("table"), headers=headers, tablefmt="pretty")
            self._console_print(tabulated_info)
            return

        self._handle_result_error("Unable to Edit the Habit", results.get('error'))


    def list(self, streak = False, f = None, d = None, c = None):
        """
        List all habits, optionally filtered by frequency, date, or completion status.

        Args:
            streak (bool, optional): If true, lists streaks of habits.
            f (str, optional): Frequency filter ("DAILY" or "WEEKLY").
            d (str, optional): Specific date to check for completion.
            c (bool, optional): Whether to filter habits based on completion for a given date.

        Behavior:
            - Calls `analytics.list_habits` with optional filters.
            - Converts ISO strings to formatted dates in user-local timezone.
            - Displays the habits in a tabulated format if available.
            - Shows an error message if no habits are found or an error occurs.
        """
        tz = self.timezone
        results = analytics.list_habits(f, d, c, tz, get_streaks=streak)

        if streak:
            headers = ["ID", "Name", "Description", "Frequency", "Date", "Last Completed On", "Current Streak", "Longest Streak"]
        else:
            headers = ["ID", "Name", "Description", "Frequency", "Date", "Last Completed On"]

        if results.get("table"):
            updated_results = self._format_iso_string_to_date(results["table"], [4, 5])
            tabulated_habits = tabulate.tabulate(updated_results, headers = headers, tablefmt="pretty")
            self._console_print(tabulated_habits)
            return

        self._handle_result_error("Sorry, No habits listed", results.get('error'))


    def streak(self, i : int = None):
        """
        Display the streak statistics for a specific habit by ID.

        Args:
            i (int, optional): The ID of the habit to view streaks for. If not provided, prompts the user.

        Behavior:
            - Retrieves the streak data using `analytics.get_streak`.
            - Formats date output in the user's timezone.
            - Displays current and longest streak information in a table.
            - Shows an error message if no data is found or the operation fails.
        """
        i = i or self._console_prompt("Please enter a habit id:")
        tz = self.timezone
        results = analytics.get_streak(i, tz)
        if results.get("table"):
            updated_results = self._format_iso_string_to_date(results["table"], [3])
            headers = ["ID", "Name", "Frequency", "Date", "Current Streak", "Longest Streak"]
            tabulated_info = tabulate.tabulate(updated_results, headers=headers, tablefmt="pretty")
            self._console_print(tabulated_info)
            return
        self._handle_result_error("Sorry, Unable to find Streak for given ID", results.get('error'))


    def consistent(self):
        """
        Show consistency metrics for all habits.

        Behavior:
            - Calls `analytics.get_consistency` using the user's current timezone.
            - Displays the consistency metrics in a table format.
            - Shows an error message if the calculation fails or no data is available.
        """
        tz = self.timezone
        results = analytics.get_consistency(tz)
        if results.get("table"):
            tabulated_info = tabulate.tabulate(results.get("table"), tablefmt="pretty")
            self._console_print(tabulated_info)
            return
        self._handle_result_error("Sorry, Unable to calculate the consistency.", results.get('error'))


    def _main_menu(self):
        """
        Display the main menu and route the user to the appropriate submenu.

        Options:
            1 - Navigate to the Habit Menu.
            2 - Navigate to the Analytics Menu.
            3 - Navigate to the Preferences Menu.
            0 - Exit the application.

        Behavior:
            - Prompts the user for a menu option.
            - Opens the selected submenu or exits on invalid input or "0".
        """
        while True:
            self._console_print("1. Habit Menu")
            self._console_print("2. Analytics Menu")
            self._console_print("3. Preferences")
            self._console_print("0. Exit")
            user_input = self._console_prompt("Please select an option")
            print("\n")
            match user_input:
                case "1":
                    self._habit_menu()
                    break
                case "2":
                    self._analytics_menu()
                    break
                case "3":
                    self._config_menu()
                    break
                case _:
                    break


    def _habit_menu(self):
        """
        Display the habit management menu and handle related user actions.

        Options:
            1 - Add a new habit.
            2 - Edit an existing habit (lists habits first).
            3 - Delete a habit (lists habits first).
            9 - Return to the main menu.
            0 - Exit the application.

        Behavior:
            - Prompts the user for a menu option.
            - Calls the appropriate habit management method based on input.
            - Returns to the main menu when "9" is selected.
        """
        while True:
            self._console_print("1. Add Habit")
            self._console_print("2. Edit Habit")
            self._console_print("3. Delete Habit")
            self._console_print("9. Go Back")
            self._console_print("0. Exit")
            user_input = self._console_prompt("Please select an option")
            print("\n")
            match user_input:
                case "1":
                    self.add()
                case "2":
                    self.list()
                    self.edit()
                case "3":
                    self.list()
                    self.delete()
                case "9":
                    self._main_menu()
                    break
                case _:
                    break


    def _analytics_menu(self):
        """
        Display the analytics menu to view habit data and performance insights.

        Options:
            1 - List all habits.
            2 - View streaks for a habit.
            3 - View the longest streak.
            4 - View the most inconsistent habit.
            9 - Return to the main menu.
            0 - Exit the application.

        Behavior:
            - Prompts the user for an analytics option.
            - Displays the relevant data using `list` or `streak` views.
            - Returns to the main menu when "9" is selected.
        """
        while True:
            self._console_print("1. List All")
            self._console_print("2. List All With Streak")
            self._console_print("3. Longest Streak")
            self._console_print("4. Consistency")
            self._console_print("9. Go Back")
            self._console_print("0. Exit")
            user_input = self._console_prompt("Please select an option")
            print("\n")
            match user_input:
                case "1":
                    self.list()
                case "2":
                    self.list(streak=True)
                case "3":
                    self.streak()
                case "4":
                    self.consistent()
                case "9":
                    self._main_menu()
                    break
                case _:
                    break


    def _config_menu(self):
        """
        Display the configuration menu for updating user preferences.

        Options:
            1 - Edit user preferences (username, timezone, terminal color).
            9 - Return to the main menu.
            0 - Exit the application.

        Behavior:
            - Allows user to update personal settings via `user(edit=True)`.
            - Refreshes local CLI settings via `_get_config` after edit.
            - Returns to the main menu when "9" is selected.
        """
        while True:
            self._console_print("1. Display User")
            self._console_print("2. Edit User")
            self._console_print("9. Go Back")
            self._console_print("0. Exit")
            user_input = self._console_prompt("Please select an option")
            print("\n")
            match user_input:
                case "1":
                    self.user()
                case "2":
                    self.user(edit=True)
                    self._console_print("\n")
                    self._get_config()
                case "9":
                    self._main_menu()
                    break
                case _:
                    break


    def run(self):
        """
        Entry point for the CLI interface.

        Behavior:
            - Displays the HabitX ASCII logo and welcome message.
            - Loads user configuration.
            - Launches the main menu.
        """
        ascii_art = pyfiglet.figlet_format("HabitX")
        self._console_print(ascii_art)
        self._console_print("Welcome, user. Habit X is here to axe your bad habits and develop healthy lifestyle.")
        self._main_menu()