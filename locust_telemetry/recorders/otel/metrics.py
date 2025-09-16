from typing import Any, Callable, List, Optional

from opentelemetry.metrics import Histogram, Meter

from locust_telemetry.core.recorder import TelemetryBaseRecorder
from locust_telemetry.recorders.otel.callbacks import (
    callback_with_recorder,
    cpu_usage_callback,
    failures_count_callback,
    failures_per_second_callback,
    memory_usage_callback,
    network_usage_callback,
    requests_count_callback,
    requests_per_second_callback,
    user_count_callback,
)


def _create_histogram(
    meter: Meter, name: str, description: str, unit: str = "ms"
) -> Histogram:
    """
    Create an OpenTelemetry histogram for recording distributions of values.

    Parameters
    ----------
    meter : Meter
        OpenTelemetry Meter used to create the histogram.
    name : str
        Name of the metric.
    description : str
        Human-readable description of the metric.
    unit : str, optional
        Unit of measurement (default is "ms").

    Returns
    -------
    Histogram
        Configured histogram instrument.
    """
    return meter.create_histogram(name=name, description=description, unit=unit)


def _create_observable_gauge(
    meter: Meter,
    name: str,
    description: str,
    unit: str = "1",
    callbacks: Optional[List[Callable]] = None,
) -> Any:
    """
    Create an OpenTelemetry Observable Gauge.

    Observable gauges capture instantaneous values, which are updated via
    callback functions.

    Parameters
    ----------
    meter : Meter
        OpenTelemetry Meter used to create the gauge.
    name : str
        Name of the metric.
    description : str
        Human-readable description of the metric.
    unit : str, optional
        Unit of measurement (default is dimensionless "1").
    callbacks : list[Callable], optional
        List of callback functions to provide gauge values.

    Returns
    -------
    Any
        Configured Observable Gauge instrument.
    """
    return meter.create_observable_gauge(
        name=name,
        description=description,
        unit=unit,
        callbacks=callbacks or [],
    )


class OtelLocustEvents:
    """
    OpenTelemetry metrics for Locust test lifecycle events.

    Records general test lifecycle timestamps as a histogram.
    """

    def __init__(self, recorder: TelemetryBaseRecorder):
        """
        Initialize test event metrics.

        Parameters
        ----------
        recorder : TelemetryBaseRecorder
            Recorder instance providing access to the Locust environment.
        """
        meter = recorder.env.otel_meter

        self.test_event = _create_histogram(
            meter, "locust.test.event", "General test lifecycle event timestamps"
        )


class OtelRequestMetrics:
    """
    OpenTelemetry metrics for Locust request-level telemetry.

    Includes request durations and observable gauges for request counts,
    failures, user counts, and request/failure rates.
    """

    def __init__(self, recorder: TelemetryBaseRecorder):
        """
        Initialize request metrics.

        Parameters
        ----------
        recorder : TelemetryBaseRecorder
            Recorder instance providing access to the Locust environment.
        """
        meter = recorder.env.otel_meter

        self.request_duration = _create_histogram(
            meter,
            "locust.requests.duration",
            "Request duration distributions",
        )

        # Observable gauges with recorder-wrapped callbacks
        self.requests_count = _create_observable_gauge(
            meter,
            "locust.requests.count",
            "Current cumulative count of executed requests",
            callbacks=[callback_with_recorder(recorder, requests_count_callback)],
        )

        self.errors_count = _create_observable_gauge(
            meter,
            "locust.requests.errors.count",
            "Current cumulative count of failed requests",
            callbacks=[callback_with_recorder(recorder, failures_count_callback)],
        )

        self.user_count = _create_observable_gauge(
            meter,
            "locust.users.count",
            "Current number of active virtual users executing requests",
            callbacks=[callback_with_recorder(recorder, user_count_callback)],
        )

        self.rps = _create_observable_gauge(
            meter,
            "locust.requests.rps",
            "Requests per second",
            callbacks=[callback_with_recorder(recorder, requests_per_second_callback)],
        )

        self.fps = _create_observable_gauge(
            meter,
            "locust.requests.fps",
            "Failures per second",
            callbacks=[callback_with_recorder(recorder, failures_per_second_callback)],
        )


class OtelSystemMetrics:
    """
    OpenTelemetry metrics for system-level telemetry.

    Collects CPU usage, memory usage, and network I/O via observable gauges.
    """

    def __init__(self, recorder: TelemetryBaseRecorder):
        """
        Initialize system metrics.

        Parameters
        ----------
        recorder : TelemetryBaseRecorder
            Recorder instance providing access to the Locust environment.
        """
        meter = recorder.env.otel_meter

        self.cpu_usage = _create_observable_gauge(
            meter,
            "locust.cpu.usage",
            "Current CPU utilization percentage",
            "%",
            callbacks=[callback_with_recorder(recorder, cpu_usage_callback)],
        )

        self.memory_usage = _create_observable_gauge(
            meter,
            "locust.memory.usage",
            "Current resident memory usage (RSS)",
            "By",
            callbacks=[callback_with_recorder(recorder, memory_usage_callback)],
        )

        self.network_bytes = _create_observable_gauge(
            meter,
            "locust.network.bytes",
            "Bytes sent/received over network",
            "By",
            callbacks=[callback_with_recorder(recorder, network_usage_callback)],
        )


class OtelMetricsDefinition:
    """
    Container for all OpenTelemetry metrics instruments.

    Aggregates event, request, and system metrics for easy access and management.
    """

    def __init__(self, recorder: TelemetryBaseRecorder):
        """
        Initialize all OpenTelemetry metrics for a recorder.

        Parameters
        ----------
        recorder : TelemetryBaseRecorder
            Recorder instance providing access to the Locust environment.
        """
        self.events = OtelLocustEvents(recorder)
        self.requests = OtelRequestMetrics(recorder)
        self.system = OtelSystemMetrics(recorder)
