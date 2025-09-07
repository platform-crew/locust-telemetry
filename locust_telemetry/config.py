"""
locust-telemetry Configuration

This module defines:
- Default interval settings for stats recording and test stop buffering
- Master and worker recorder class references

Constants:
- DEFAULT_OB_RECORDER_INTERVAL: default interval (seconds) for recording stats
- DEFAULT_OB_WAIT_AFTER_TEST_STOP: buffer time after test stop (seconds)
  for log visualization

"""

from datetime import datetime, timezone
from typing import Callable, Dict

# Default intervals
DEFAULT_RECORDER_INTERVAL = 2  # seconds


ENVIRONMENT_METADATA: Dict[str, Callable] = {
    "run_id": lambda: datetime.now(timezone.utc).isoformat()
}
