"""
Logging configuration for locust-observability.

Outputs structured JSON logs with RFC3339 timestamps.
"""

import logging
from datetime import datetime, timezone

from pythonjsonlogger.json import JsonFormatter

# -------------------------------
# Custom RFC3339 JSON Formatter
# -------------------------------


class RFC3339JsonFormatter(JsonFormatter):
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

# TODO: Change it to env variable
# TODO: Also, telemetry logging should always set to info
LOG_LEVEL = "INFO"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": RFC3339JsonFormatter,
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "rename_fields": {"asctime": "time", "levelname": "level"},
            "json_indent": None,  # single-line JSON
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
        "handlers": ["null"],  # Disable root logger output
        "level": "WARNING",  # keep root quiet
    },
    "loggers": {
        "locust_telemetry": {  # Only this plugin namespace
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,  # prevent double logging to root
        },
    },
}


def configure_logging():
    """Apply the LOGGING_CONFIG to the Python logging system."""
    logging.config.dictConfig(LOGGING_CONFIG)
