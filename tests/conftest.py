import pytest
from peewee import SqliteDatabase
from habit_tracker.models import Habit, Config, Activity

test_db = SqliteDatabase(":memory:")

@pytest.fixture(autouse=True)
def setup_and_teardown():
    test_db.bind([Habit, Activity, Config], bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables([Habit, Activity, Config])

    with test_db.atomic() as txn:
        yield  # Run the test
        txn.rollback()  # Rollback after test

    test_db.drop_tables([Habit, Activity, Config])
    test_db.close()
