import logging

from locust_observability.logger import RFC3339JsonFormatter


def test_rfc3339_formatter_outputs_utc_timestamp():
    """Ensure RFC3339JsonFormatter formats timestamp with milliseconds and Z suffix."""
    formatter = RFC3339JsonFormatter(fmt="%(asctime)s %(message)s")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="hello",
        args=(),
        exc_info=None,
    )
    formatted = formatter.formatTime(record)
    # It should end with 'Z' (Zulu / UTC)
    assert formatted.endswith("Z")
    # Should contain milliseconds
    assert "." in formatted.split("T")[1]
