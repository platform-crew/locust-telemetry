"""
locust-telemetry Configuration
===============================

This module defines default settings and references for Locust telemetry recorders.

Modules
-------
- Default interval settings for stats recording.

Constants
---------
DEFAULT_RECORDER_INTERVAL : int
    Default interval in seconds for recording stats.

ENVIRONMENT_METADATA : Dict[str, Callable]
    Dictionary of environment metadata functions. For example, 'run_id' returns
    the current UTC timestamp in ISO format.
"""

from datetime import datetime, timezone
from typing import Callable, Dict

# Default interval for telemetry recording
DEFAULT_RECORDER_INTERVAL: int = 2  # seconds

ENVIRONMENT_METADATA: Dict[str, Callable] = {
    "run_id": lambda: datetime.now(timezone.utc).isoformat()
}
