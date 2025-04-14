"""
Habit Tracker PeeWee Module and DB Functions
==============================

This module defines the structure and operations for a Habit Tracker database system using the `peewee` ORM and SQLite. The module supports managing habits, tracking their activities, and configuring user-specific settings like timezone and preferred color. It also provides the functionality for initializing and migrating the database schema. This module utilizes both functional and OOP paradigms.

Dependencies:
-------------
- `pytz`: for timezone handling (UTC used by default)
- `os`: for file path manipulation
- `json`: for parsing demo data
- `datetime`: for handling datetime fields
- `peewee`: for ORM interaction with SQLite

Database Schema:
----------------
The database consists of three primary models:
1. `Habit`: Represents a habit, including its name, description, frequency (daily/weekly), creation and update timestamps, and the last completion date.
2. `Activity`: Tracks the completion of a habit on specific dates.
3. `Config`: Stores user-specific settings such as username, preferred color, and timezone.

Database Migration:
-------------------
The database schema is versioned. The current version is stored in the SQLite database using the `PRAGMA user_version` command. When initializing the database for the first time, the migration process will populate it with demo data.

Functions:
----------
- `parse_datetime(date_str)`: Converts a datetime string in the format `YYYY-MM-DD HH:MM:SS` into a timezone-aware `datetime` object in UTC. Returns `None` if the string is empty.
- `get_demo_data()`: Loads and parses demo habit data from a `demo.json` file located in the project directory.
- `add_demo_data_to_db(data)`: Adds the demo habit data to the database. It creates habit entries and associated activity records.
- `migrate_to_db_1()`: Migrates the database schema to version 1. Creates the tables `Config`, `Habit`, and `Activity`, and populates the database with demo data if no entries are present.
- `init_db()`: Initializes the database by connecting to the SQLite file and checking the schema version. If necessary, it migrates the schema to version 1 and loads demo data.

Classes:
--------
- `BaseModel`: A base class that all models inherit from. It specifies the database connection.
- `Habit`: Represents a habit with attributes like name, description, frequency (DAILY/WEEKLY), creation and update timestamps, and the last completion date.
- `Activity`: Represents an activity record for a habit, including the date it was completed.
- `Config`: Stores user configuration such as username, color, and timezone.

Example Usage:
--------------
To initialize the database, use the `init_db()` function. It will check the database version and perform any necessary migrations.

>>> init_db()

After initialization, you can start using the `Habit`, `Activity`, and `Config` models to interact with the database.

Notes:
------
- The demo data is loaded from a file named `demo.json` and is expected to be structured in a specific format.
- The default timezone used for all datetimes is UTC, but users can configure their own timezone in the `Config` model.

"""
import pytz
import os
import json
from datetime import datetime
from peewee import SqliteDatabase, Model, CharField, DateTimeField, ForeignKeyField, IntegerField

# Defining the version of the database schema, for future changes
# 'habits.db' is the file name of the SQLite database
# `pragmas={'foreign_keys': 1}` is a SQLite-specific code, this ensures clear TABLE RELATIONS
DB_VERSION = 1
# db = SqliteDatabase('habits.db', pragmas={'foreign_keys': 1})
db_path = os.path.join(os.path.expanduser("~"), ".habitx", "habit.db")
os.makedirs(os.path.dirname(db_path), exist_ok=True)
db = SqliteDatabase(db_path)

class BaseModel(Model):
    """
    Base model that other database models will inherit.
    The 'Meta' class inside the BaseModel defines the database connection.
    The 'database' attribute is set to 'db', which means all models using this base class will use the 'habits.db' database.
    This ensures all MODELS will connect to the same 'habits.db' database
    """

    class Meta:
        database = db


class Habit(BaseModel):
    """
    Represents a habit in the database.

    Attributes:
        id (int): Primary key for the habit.
        name (str): The name of the habit.
        description (str): A description of the habit.
        frequency (str): Frequency of the habit (DAILY or WEEKLY).
        created_at (datetime): The timestamp when the habit was created.
        updated_at (datetime): The timestamp when the habit was last updated.
        last_completed_at (datetime): The timestamp when the habit was last completed.
    """
    id = IntegerField(primary_key=True)
    name = CharField()
    description = CharField()
    frequency = CharField(choices=[("DAILY", "Daily"), ("WEEKLY", "Weekly")])
    created_at = DateTimeField(default=lambda: datetime.now(pytz.UTC))
    updated_at = DateTimeField(default=lambda: datetime.now(pytz.UTC))
    last_completed_at = DateTimeField(null=True)


class Activity(BaseModel):
    """
    Represents an activity for a specific habit.

    Attributes:
        habit (ForeignKeyField): Foreign key to the `Habit` model.
        completed_at (datetime): The timestamp when the activity was completed.
    """
    habit = ForeignKeyField(Habit, backref='activities', on_delete='CASCADE')
    completed_at = DateTimeField()


class Config(BaseModel):
    """
    Stores user-specific configuration.

    Attributes:
        username (str): The username of the user.
        created_at (datetime): The timestamp when the config was created.
        color (str): The user's preferred color.
        timezone (str): The user's preferred timezone.
    """
    username = CharField(unique=True)
    created_at = DateTimeField(default=lambda: datetime.now(pytz.UTC))
    color = CharField(default='blue')
    timezone = CharField(default='UTC')


# Functions to be utilized
def parse_datetime(date_str):
    """
    Converts a datetime string in the format `YYYY-MM-DD HH:MM:SS` to a timezone-aware `datetime` object in UTC.

    Args:
        date_str (str): The datetime string to be parsed.

    Returns:
        datetime: The parsed timezone-aware datetime object, or None if the input is empty.
    """
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.UTC)
    return None


def get_demo_data():
    """
    Loads and parses demo habit data from a JSON file.

    Returns:
        list: A list of habit data dictionaries.
    """
    json_path = os.path.dirname(__file__) + os.path.sep + "../demo.json"
    with open(json_path) as json_file:
        data = json.load(json_file)
        return data["habits"]


def add_demo_data_to_db(data):
    """
    Adds demo habit data to the database.

    Args:
        data (list): A list of habit data dictionaries.
    """
    with db.atomic():
        for habit_data in data:
            habit = Habit.create(
                name=habit_data["name"],
                description=habit_data["description"],
                frequency=habit_data["frequency"],
                created_at=parse_datetime(habit_data["created_at"]),
                updated_at=parse_datetime(habit_data["updated_at"]),
                last_completed_at=parse_datetime(habit_data["last_completed_at"]),
            )

            for date in habit_data["completed_dates"]:
                Activity.create(habit=habit.id, completed_at=parse_datetime(date))

            print(f"Added the Habit with ID: {habit.id}")


def add_default_config_to_db():
    """
    Adds default configuration to the database.
    """
    with db.atomic():
        Config.create(
            username="user",
            timezone="UTC",
            color="blue",
        )
    print("Made the default user configuration for the Habit.")


# Migration to DB VERSION
def migrate_to_db_1():
    """
    Migrates the database schema to version 1. Creates the necessary tables and adds demo data if the database is empty.
    """
    db.create_tables([Config, Habit, Activity])
    if Habit.select().count() == 0 and Config.select().count() == 0:
        print("Setting up database for the first time...")
        habits_data = get_demo_data()
        add_demo_data_to_db(habits_data)
        add_default_config_to_db()
    print("Database initialized.")


def init_db():
    """
    Initializes the database by checking the schema version. If necessary, performs migrations and sets up demo data.
    """
    db.connect()
    version = db.execute_sql("PRAGMA user_version").fetchone()[0]

    if version == DB_VERSION:
        return

    if version == 0:
        migrate_to_db_1()
        db.execute_sql("PRAGMA user_version = 1")

    db.close()