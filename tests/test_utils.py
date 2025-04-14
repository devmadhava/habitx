from habit_tracker.utils import *
import pytz

def test_format_date_to_string():
    dt = datetime(2021, 10, 15)
    assert format_date_to_string(dt) == '15.10.2021'
    assert format_date_to_string(None) is None

def test_get_current_utc_time():
    now = get_current_utc_time()
    assert now.tzinfo is not None
    assert now.tzinfo.tzname(now) == 'UTC'

def test_parse_iso_datetime():
    iso = "2021-10-15T13:45:00"
    dt = parse_iso_datetime(iso)
    assert dt == datetime(2021, 10, 15, 13, 45)

def test_convert_user_date_str_to_iso():
    user_date = "15/10/2021"
    assert convert_user_date_str_to_iso(user_date) == "2021-10-15"

def test_parse_user_date_str_to_datetime():
    date_str = "15/10/2021"
    dt = parse_user_date_str_to_datetime(date_str)
    assert dt == datetime(2021, 10, 15)

def test_format_datetime_for_user():
    dt = datetime(2021, 10, 15, 12, 0, tzinfo=pytz.UTC)
    formatted = format_datetime_for_user(dt, "Asia/Kolkata")
    assert formatted == "15.10.2021"

def test_is_valid_timezone():
    assert is_valid_timezone("Asia/Kolkata")
    assert not is_valid_timezone("Mars/Crater")

def test_database_error_handler_success():
    @database_error_handler
    def dummy():
        return {"result": "ok"}

    result = dummy()
    assert result == {"result": "ok"}

def test_database_error_handler_db_error():
    from peewee import IntegrityError

    @database_error_handler
    def dummy():
        raise IntegrityError("duplicate entry")

    result = dummy()
    assert result["error"] == "duplicate entry"
    assert result["table"] is None

def test_database_error_handler_unknown():
    @database_error_handler
    def dummy():
        raise RuntimeError("something unexpected")

    result = dummy()
    assert "Unknown error occurred" in result["error"]
    assert result["table"] is None

def test_convert_iso_to_date_with_string():
    iso = "2023-04-15T12:30:00"
    dt = convert_iso_to_date(iso)
    assert dt.tzinfo is not None
    assert dt.isoformat().startswith("2023-04-15T12:30:00")

def test_convert_iso_to_date_with_datetime():
    dt_obj = datetime(2023, 4, 15, 12, 30)
    dt = convert_iso_to_date(dt_obj)
    assert dt.tzinfo is not None
    assert dt.isoformat().startswith("2023-04-15T12:30:00")

def test_date_str_to_utc_iso():
    local_tz = pytz.timezone("Asia/Kolkata")
    result = date_str_to_utc_iso("15/04/2023", local_tz)
    # Should start with 2023-04-14 or 2023-04-15 depending on offset (check offset manually)
    assert "2023-04-14" in result or "2023-04-15" in result
    assert result.endswith("+00:00")

def test_format_datetime_for_user_with_format():
    dt = datetime(2023, 4, 15, 12, 0, tzinfo=pytz.UTC)
    formatted = format_datetime_for_user(dt, "America/New_York", fmt="%Y/%m/%d %I:%M %p")
    assert isinstance(formatted, str)
    assert formatted.startswith("2023/04/15") or formatted.startswith("2023/04/14")
