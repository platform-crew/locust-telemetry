"""
OpenTelemetry metrics definitions for Locust telemetry integration.

Responsibilities
----------------
- Provide a unified registry of metric instruments for Locust test runs.
- Expose helpers to construct OpenTelemetry histograms, counters, and gauges.
- Organize metrics into domains: test lifecycle events, request metrics, and
  system metrics.
- Ensure consistency in metric naming, description, and units.

Usage
-----
Instantiate :class:`OtelMetricsDefinition` to access grouped metrics:

>>> metrics = OtelMetricsDefinition()
>>> metrics.requests.requests_counter.add(1, attributes={"endpoint": "/api"})

Notes
-----
- Metric instruments are created once at module load time using the global OTel meter.
- This module is used by recorders (e.g. MasterLocustOtelRecorder) to publish metrics.
"""

from opentelemetry import metrics

from locust_telemetry import config

# Global meter instance for all metrics
meter = metrics.get_meter(config.TELEMETRY_OTEL_METRICS_METER)


def _create_histogram(name: str, description: str, unit: str = "ms"):
    """
    Create an OpenTelemetry Histogram instrument.

    Parameters
    ----------
    name : str
        Metric name (dot-delimited, e.g. ``locust.requests.duration``).
    description : str
        Human-readable description of the metric.
    unit : str, default="ms"
        Measurement unit (milliseconds by default).

    Returns
    -------
    Histogram
        OpenTelemetry histogram metric instrument.
    """
    return meter.create_histogram(name=name, description=description, unit=unit)


def _create_counter(name: str, description: str, unit: str = "1"):
    """
    Create an OpenTelemetry Counter instrument.

    Parameters
    ----------
    name : str
        Metric name (dot-delimited).
    description : str
        Human-readable description of the metric.
    unit : str, default="1"
        Measurement unit (dimensionless by default).

    Returns
    -------
    Counter
        OpenTelemetry counter metric instrument.
    """
    return meter.create_counter(name=name, description=description, unit=unit)


def _create_gauge(name: str, description: str, unit: str = "1"):
    """
    Create an OpenTelemetry Observable Gauge instrument.

    Parameters
    ----------
    name : str
        Metric name (dot-delimited).
    description : str
        Human-readable description of the metric.
    unit : str, default="1"
        Measurement unit (dimensionless by default).

    Returns
    -------
    ObservableGauge
        OpenTelemetry observable gauge metric instrument.
    """
    return meter.create_observable_gauge(name=name, description=description, unit=unit)


class OtelLocustEvents:
    """
    Telemetry histograms for Locust test lifecycle events.

    Responsibilities
    ----------------
    - Provide timestamped markers for test phases and critical events.
    - Enable correlation of lifecycle events with performance results.

    Metrics emitted
    ---------------
    - ``locust.test.start`` : Timestamp of test start events.
    - ``locust.test.stop`` : Timestamp of test stop events.
    - ``locust.test.spawn_complete`` : Timestamp of spawning complete events.
    - ``locust.test.cpu_warning`` : CPU warning events with annotation.
    - ``locust.test.event`` : General test lifecycle annotations.
    - ``locust.test.failure`` : Test-level failure or crash annotations.
    """

    def __init__(self):
        self.test_start_event = _create_histogram(
            "locust.test.start", "Timestamp of test start events for annotations"
        )
        self.test_stop_event = _create_histogram(
            "locust.test.stop", "Timestamp of test stop events for annotations"
        )
        self.spawn_complete_event = _create_histogram(
            "locust.test.spawn_complete",
            "Timestamp of spawn complete events for annotations",
        )
        self.cpu_warning_event = _create_histogram(
            "locust.test.cpu_warning",
            "Test lifecycle CPU warning events with type annotation",
        )
        self.test_event = _create_histogram(
            "locust.test.event", "General test lifecycle events with type annotation"
        )
        self.test_failure_event = _create_histogram(
            "locust.test.failure",
            "Timestamp and annotations for test-level failures or crashes",
        )


class OtelRequestMetrics:
    """
    Telemetry counters, histograms, and gauges for Locust request metrics.

    Responsibilities
    ----------------
    - Track request volumes, errors, and response characteristics.
    - Measure active users and in-flight requests.
    - Provide distributions for response times and payload sizes.

    Metrics emitted
    ---------------
    - ``locust.requests.count`` : Total number of requests made.
    - ``locust.requests.errors.count`` : Total number of failed requests.
    - ``locust.requests.in_progress`` : Number of requests currently in progress.
    - ``locust.requests.duration`` : Distribution of request response times (ms).
    - ``locust.requests.response_size`` : Distribution of response sizes (bytes).
    - ``locust.user.count`` : Current number of active Virtual Users.
    - ``locust.user.spawned`` : Total number of Virtual Users spawned.
    - ``locust.user.despawned`` : Total number of Virtual Users stopped.
    """

    def __init__(self):
        self.requests_counter = _create_counter(
            "locust.requests.count", "Total number of requests made"
        )
        self.errors_counter = _create_counter(
            "locust.requests.errors.count", "Total number of failed requests"
        )
        self.requests_in_progress = _create_counter(
            "locust.requests.in_progress", "Number of requests currently in progress"
        )
        self.request_duration = _create_histogram(
            "locust.requests.duration", "Distribution of request response times"
        )
        self.response_size = _create_histogram(
            "locust.requests.response_size", "Distribution of response sizes", unit="By"
        )
        self.user_count_gauge = _create_gauge(
            "locust.user.count", "Current number of active Virtual Users"
        )
        self.user_spawn_counter = _create_counter(
            "locust.user.spawned", "Total number of Virtual Users spawned"
        )
        self.user_despawn_counter = _create_counter(
            "locust.user.despawned", "Total number of Virtual Users stopped"
        )


class OtelSystemMetrics:
    """
    Telemetry gauges for system-level metrics.

    Responsibilities
    ----------------
    - Track CPU, memory, and network usage of the Locust runner process.
    - Provide real-time observability into system resource consumption.

    Metrics emitted
    ---------------
    - ``locust.cpu.usage`` : CPU usage percentage of the Locust runner process.
    - ``locust.memory.usage`` : Resident memory usage (RSS) in bytes.
    - ``locust.network.bytes_sent`` : Total bytes sent by the Locust process.
    - ``locust.network.bytes_received`` : Total bytes received by the Locust process.
    """

    def __init__(self):
        self.cpu_usage_gauge = _create_gauge(
            "locust.cpu.usage", "CPU usage percentage of the Locust runner process", "%"
        )
        self.memory_usage_gauge = _create_gauge(
            "locust.memory.usage",
            "Memory usage (RSS) of the Locust runner process",
            "By",
        )
        self.network_bytes_sent = _create_gauge(
            "locust.network.bytes_sent",
            "Total number of bytes sent by the Locust runner process",
            "By",
        )
        self.network_bytes_received = _create_gauge(
            "locust.network.bytes_received",
            "Total number of bytes received by the Locust runner process",
            "By",
        )


class OtelMetricsDefinition:
    """
    Combined interface for all Locust OpenTelemetry metrics.

    Responsibilities
    ----------------
    - Group metrics into three domains:
      * ``events`` : Test lifecycle events
      * ``requests`` : Request-related metrics
      * ``system`` : System-level process metrics
    - Provide a single access point for all metrics used by recorders.
    """

    def __init__(self):
        self.events = OtelLocustEvents()
        self.requests = OtelRequestMetrics()
        self.system = OtelSystemMetrics()
