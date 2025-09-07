"""
Logging configuration for locust-observability
==============================================

This module provides structured JSON logging for Locust Telemetry.

Features
--------
- Outputs logs in JSON format compatible with RFC3339 timestamps.
- Custom formatter for millisecond-precision timestamps in UTC.
- Configures loggers specifically for the `locust_telemetry` namespace.
- Provides a convenience function to apply the logging configuration.

Classes
-------
RFC3339JsonFormatter
    Custom JSON formatter that outputs timestamps in RFC3339 format with
    millisecond precision.

Functions
---------
configure_logging()
    Apply the logging configuration to the Python logging system.
"""

import logging
from datetime import datetime, timezone

from pythonjsonlogger.json import JsonFormatter

# -------------------------------
# Custom RFC3339 JSON Formatter
# -------------------------------


class RFC3339JsonFormatter(JsonFormatter):
    """
    Custom JSON formatter for RFC3339 timestamps.

    This formatter ensures timestamps are:
    - in ISO 8601 / RFC3339 format
    - millisecond-precision
    - in UTC (Z suffix)
    """

    def formatTime(self, record, datefmt=None) -> str:
        """
        Format the log record timestamp in RFC3339 with milliseconds.

        Args:
            record (logging.LogRecord): Log record to format
            datefmt (Optional[str]): Ignored; kept for compatibility

        Returns:
            str: ISO 8601 formatted timestamp
        """
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


# -------------------------------
# Logging Configuration
# -------------------------------

LOG_LEVEL = "INFO"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": RFC3339JsonFormatter,
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "rename_fields": {"asctime": "time", "levelname": "level"},
            "json_indent": None,
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "level": LOG_LEVEL,
        },
        "null": {
            "class": "logging.NullHandler",
            "level": LOG_LEVEL,
        },
    },
    "root": {
        "handlers": ["null"],
        "level": "WARNING",
    },
    "loggers": {
        "locust_telemetry": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


def configure_logging():
    """
    Apply the logging configuration to the Python logging system.

    Sets up JSON logging for `locust_telemetry` and disables output
    from the root logger.
    """
    logging.config.dictConfig(LOGGING_CONFIG)
