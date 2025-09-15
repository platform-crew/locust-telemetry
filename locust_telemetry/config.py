"""
This module defines default settings and references for Locust telemetry recorders.

Constants
---------
DEFAULT_RECORDER_INTERVAL : int
    Default interval in seconds for recording stats is 2 seconds. But can be set through
    environment variable LOCUST_TELEMETRY_RECORDER_INTERVAL

DEFAULT_ENVIRONMENT_METADATA : Dict[str, Callable]
    Dictionary of environment metadata functions. For example, 'run_id' returns
    the current UTC timestamp in ISO format. This is for internal use only.

TELEMETRY_CLI_GROUP_NAME: str
    Configuration cli group to add all the necessary args to locust-telemetry
"""

import uuid
from typing import Callable, Dict

# Default interval for telemetry stats recording
DEFAULT_STATS_RECORDER_INTERVAL: int = 2  # seconds

# Default interval for system usage recording
DEFAULT_SYSTEM_USAGE_RECORDER_INTERVAL: int = 3  # 2 seconds

# Configuration cli group to add all the necessary args
TELEMETRY_CLI_GROUP_NAME: str = "locust-telemetry"

# Environment metadata which can be access by environment.<metadata>
DEFAULT_ENVIRONMENT_METADATA: Dict[str, Callable] = {
    "run_id": lambda: str(uuid.uuid4())[:8]  # first 8 characters of UUID
}

TELEMETRY_JSON_STATS_RECORDER_PLUGIN_ID = "stats-json"

TELEMETRY_OTEL_RECORDER_PLUGIN_ID = "otel"

TELEMETRY_OTEL_METRICS_METER = "locust_telemetry"
