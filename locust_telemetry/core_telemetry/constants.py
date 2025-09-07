"""
Locust Telemetry Constants
==========================

This module defines constants for telemetry events and metrics
used within Locust Telemetry plugins and recorders.

Classes
-------
LocustTestEvent
    Enumeration of events emitted during the Locust test lifecycle.

RequestMetric
    Enumeration of metrics collected for HTTP requests and endpoints.
"""

from locust_telemetry.common.telemetry import BaseTelemetryEnum, TelemetryData


class LocustTestEvent(BaseTelemetryEnum):
    """
    Telemetry events emitted during the test lifecycle.

    Attributes
    ----------
    START : TelemetryData
        Emitted when a test starts.
    STOP : TelemetryData
        Emitted when a test stops.
    SPAWN_COMPLETE : TelemetryData
        Emitted when user spawn is complete.
    CPU_WARNING : TelemetryData
        Emitted when CPU usage exceeds threshold.
    """

    START = TelemetryData("event", "event.test.start")
    STOP = TelemetryData("event", "event.test.stop")
    SPAWN_COMPLETE = TelemetryData("event", "event.spawn.complete")
    CPU_WARNING = TelemetryData("event", "event.cpu.warning")


class RequestMetric(BaseTelemetryEnum):
    """
    Metrics collected for HTTP requests and endpoints.

    Attributes
    ----------
    CURRENT_STATS : TelemetryData
        Real-time request statistics during the test.
    FINAL_STATS : TelemetryData
        Final aggregated request statistics at test end.
    ENDPOINT_STATS : TelemetryData
        Per-endpoint statistics collected.
    ENDPOINT_ERRORS : TelemetryData
        Per-endpoint error statistics.
    """

    CURRENT_STATS = TelemetryData("metric", "metric.request.current.stats")
    FINAL_STATS = TelemetryData("metric", "metric.request.final.stats")
    ENDPOINT_STATS = TelemetryData("metric", "metric.request.endpoint.stats")
    ENDPOINT_ERRORS = TelemetryData("metric", "metric.request.endpoint.errors")
