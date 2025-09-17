from collections import namedtuple
from enum import Enum

#: Named tuple for OpenTelemetry metric definitions.
#:
#: Attributes
#: ----------
#: name : str
#:     The OpenTelemetry metric name (fully qualified).
#: description : str
#:     Human-readable description of what the metric represents.
MetricInfo = namedtuple("MetricInfo", ["name", "description"])


class OtelMetricDefinition(Enum):
    """
    Enumeration of all OpenTelemetry metric definitions used
    in the Locust Telemetry integration.

    Each member wraps a :class:`MetricInfo` containing:
      - ``name``: The OpenTelemetry metric name string.
      - ``description``: A human-readable explanation of the metric.

    These definitions are used consistently across handlers to ensure
    naming standardization, discoverability, and consistent telemetry output.
    """

    TEST_EVENTS = MetricInfo(
        "locust.test.events",
        "General test lifecycle event timestamps",
    )
    """Lifecycle event timestamps (e.g., test start, stop)."""

    NETWORK_BYTES = MetricInfo(
        "locust.network.bytes",
        "Bytes sent/received over network",
    )
    """Cumulative network I/O in bytes, split by direction (sent/received)."""

    MEMORY_USAGE = MetricInfo(
        "locust.memory.usage",
        "Current resident memory usage (RSS)",
    )
    """Resident memory usage (RSS) of the Locust process in MiB."""

    CPU_USAGE = MetricInfo(
        "locust.cpu.usage",
        "Current CPU utilization percentage",
    )
    """CPU utilization percentage of the Locust process."""

    REQUEST_DURATION = MetricInfo(
        "locust.requests.duration",
        "Request duration distributions",
    )
    """Distribution of request response times in milliseconds."""

    REQUEST_COUNT = MetricInfo(
        "locust.requests.count",
        "Current cumulative count of executed requests",
    )
    """Cumulative count of all executed requests."""

    ERROR_COUNT = MetricInfo(
        "locust.requests.errors.count",
        "Current cumulative count of failed requests",
    )
    """Cumulative count of all failed requests."""

    USER_COUNT = MetricInfo(
        "locust.users.count",
        "Current number of active virtual users executing requests",
    )
    """Number of currently active virtual users running in the test."""

    RPS = MetricInfo(
        "locust.requests.rps",
        "Requests per second",
    )
    """Requests executed per second (throughput)."""

    FPS = MetricInfo(
        "locust.requests.fps",
        "Failures per second",
    )
    """Failures observed per second (failure rate)."""

    @property
    def metric_name(self) -> str:
        """
        Return the OpenTelemetry metric name string.

        Returns
        -------
        str
            The fully qualified OpenTelemetry metric name.
        """
        return self.value.name

    @property
    def metric_description(self) -> str:
        """
        Return the human-readable description of the metric.

        Returns
        -------
        str
            The description associated with the metric definition.
        """
        return self.value.description
