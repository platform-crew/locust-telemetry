import json
import logging
from datetime import datetime, timezone

from locust_telemetry.logger import LOGGING_CONFIG, RFC3339JsonFormatter


def test_rfc3339_json_formatter_outputs_rfc3339_timestamp():
    """
    Verify that RFC3339JsonFormatter outputs timestamps with milliseconds
    and Zulu timezone.
    """
    formatter = RFC3339JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="test message",
        args=None,
        exc_info=None,
    )
    # Manually set a known timestamp
    record.created = 1690000000.123456  # arbitrary epoch float
    formatted_time = formatter.formatTime(record)
    dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
    expected_time = dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    assert formatted_time == expected_time


def test_formatter_outputs_json_with_required_fields():
    """Ensure formatter produces JSON containing the renamed fields."""
    formatter = RFC3339JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"asctime": "time", "levelname": "level"},
    )
    record = logging.LogRecord(
        name="test_logger",
        level=logging.WARNING,
        pathname=__file__,
        lineno=10,
        msg="hello json",
        args=None,
        exc_info=None,
    )
    json_str = formatter.format(record)
    data = json.loads(json_str)
    # Check required fields are present
    assert "time" in data
    assert "level" in data
    assert "name" in data
    assert "message" in data
    assert data["message"] == "hello json"


def test_logging_config_root_and_locust_logger_levels():
    """
    Ensure LOGGING_CONFIG has root disabled and locust_telemetry configured properly.
    """
    root_cfg = LOGGING_CONFIG["root"]
    locust_cfg = LOGGING_CONFIG["loggers"]["locust_telemetry"]

    assert root_cfg["handlers"] == ["null"]
    assert root_cfg["level"] == "WARNING"

    assert locust_cfg["handlers"] == ["console"]
    assert locust_cfg["propagate"] is False
