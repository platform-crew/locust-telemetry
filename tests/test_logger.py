import json
import logging
from datetime import datetime, timezone

import pytest

from locust_telemetry.logger import RFC3339JsonFormatter, configure_logging


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


def test_default_logging_configuration():
    configure_logging()
    logger = logging.getLogger("locust_telemetry")

    # Logger level
    assert logger.level == logging.INFO

    # Logger handlers
    handler_types = [type(h) for h in logger.handlers]
    assert logging.StreamHandler in handler_types

    # Logger propagation
    assert logger.propagate is False


@pytest.mark.parametrize(
    "level,expected",
    [
        ("DEBUG", logging.DEBUG),
        ("WARNING", logging.WARNING),
        ("ERROR", logging.ERROR),
    ],
)
def test_custom_logging_levels(level, expected):
    configure_logging(level=level)
    logger = logging.getLogger("locust_telemetry")

    # Logger level
    assert logger.level == expected

    # Handler levels
    for h in logger.handlers:
        assert h.level == expected
