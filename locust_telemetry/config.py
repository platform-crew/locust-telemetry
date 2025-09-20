"""
This module defines default settings and references for Locust telemetry recorders.

Constants
---------
DEFAULT_STATS_RECORDER_INTERVAL : int
    Default interval in seconds for recording telemetry stats. The default is `3`
    seconds but may be overridden by configuration or environment variables.

DEFAULT_ENVIRONMENT_METADATA : dict[str, Callable]
    Dictionary of environment metadata providers. Each key is a metadata field name,
    and each value is a callable that produces the metadata value. For example,
    `'run_id'` returns a short UUID string.

TELEMETRY_CLI_GROUP_NAME : str
    Name of the CLI argument group for telemetry-related options.

TELEMETRY_JSON_STATS_RECORDER_PLUGIN_ID : str
    Plugin identifier for the JSON stats recorder.

TELEMETRY_OTEL_RECORDER_PLUGIN_ID : str
    Plugin identifier for the OpenTelemetry stats recorder.

TELEMETRY_OTEL_METRICS_METER : str
    Default name of the OpenTelemetry metrics meter.

TELEMETRY_SERVICE_NAME : str
    Default name of the telemetry service.

OTEL_EXPORTER_TIMEOUT : int
    Timeout in seconds for OpenTelemetry metric exporter requests.
"""

import uuid
from typing import Callable, Dict

#: Default interval (in seconds) for telemetry stats recording.
DEFAULT_STATS_RECORDER_INTERVAL: int = 3

#: Configuration CLI group to add all the necessary arguments.
TELEMETRY_CLI_GROUP_NAME: str = "locust-telemetry"

#: Environment metadata providers, accessed as `environment.<metadata>`.
DEFAULT_ENVIRONMENT_METADATA: Dict[str, Callable[[], str]] = {
    "run_id": lambda: str(uuid.uuid4())[:8]  # first 8 characters of UUID
}

#: Plugin identifier for the JSON stats recorder.
TELEMETRY_JSON_STATS_RECORDER_PLUGIN_ID: str = "stats-json"

#: Plugin identifier for the OpenTelemetry stats recorder.
TELEMETRY_OTEL_RECORDER_PLUGIN_ID: str = "stats-otel"

#: Default OpenTelemetry metrics meter name.
TELEMETRY_OTEL_METRICS_METER: str = "locust_telemetry"

#: Default service name used in OpenTelemetry resources.
TELEMETRY_SERVICE_NAME: str = "locust_telemetry"

#: Timeout (in seconds) for OpenTelemetry metric exporter requests.
OTEL_EXPORTER_TIMEOUT: int = 10
