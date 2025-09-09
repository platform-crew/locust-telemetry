"""
This module defines default settings and references for Locust telemetry recorders.

Constants
---------
DEFAULT_RECORDER_INTERVAL : int
    Default interval in seconds for recording stats is 2 seconds. But can be set through
    environment variable LOCUST_TELEMETRY_RECORDER_INTERVAL

ENVIRONMENT_METADATA : Dict[str, Callable]
    Dictionary of environment metadata functions. For example, 'run_id' returns
    the current UTC timestamp in ISO format. This is for internal use only.
"""

import uuid
from typing import Callable, Dict

# Default interval for telemetry recording
DEFAULT_RECORDER_INTERVAL: int = 2  # seconds

ENVIRONMENT_METADATA: Dict[str, Callable] = {
    "run_id": lambda: str(uuid.uuid4())[:8]  # first 8 characters of UUID
}
