"""
Logging configuration for locust-observability.

Outputs structured JSON logs with RFC3339 timestamps.
"""
import logging
import os
from datetime import datetime, timezone
from pythonjsonlogger import jsonlogger

# -------------------------------
# Custom RFC3339 JSON Formatter
# -------------------------------


class RFC3339JsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that outputs timestamps in RFC3339 format with
    millisecond precision.
    """

    def formatTime(self, record, datefmt=None) -> str:
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        # ISO 8601 / RFC3339 with milliseconds and Zulu indicator
        return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


# -------------------------------
# Logging Configuration
# -------------------------------

LOG_LEVEL = os.getenv("LOCUST_OB_LOG_LEVEL", "INFO").upper()

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": RFC3339JsonFormatter,
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "rename_fields": {"asctime": "time", "levelname": "level"},
            "json_indent": None,  # single-line JSON for observability tools
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
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        # Optional: configure third-party libraries to reduce noise
        "urllib3": {"level": "WARNING"},
        "requests": {"level": "WARNING"},
    },
}


def configure_logging():
    """Apply the LOGGING_CONFIG to the Python logging system."""
    logging.config.dictConfig(LOGGING_CONFIG)
