from opentelemetry.metrics import Meter


def _create_histogram(meter: Meter, name: str, description: str, unit: str = "ms"):
    """
    Create an OpenTelemetry Histogram instrument.

    Parameters
    ----------
    meter : Meter
        The OpenTelemetry meter used to create the histogram.
    name : str
        The metric name (dot-delimited, e.g., "locust.requests.duration").
    description : str
        Human-readable description of the metric.
    unit : str, default="ms"
        Unit of measurement (milliseconds by default).

    Returns
    -------
    Histogram
        An OpenTelemetry histogram instrument.
    """
    return meter.create_histogram(name=name, description=description, unit=unit)


def _create_counter(meter: Meter, name: str, description: str, unit: str = "1"):
    """
    Create an OpenTelemetry Counter instrument.

    Parameters
    ----------
    meter : Meter
        The OpenTelemetry meter used to create the counter.
    name : str
        The metric name (dot-delimited, e.g., "locust.requests.count").
    description : str
        Human-readable description of the metric.
    unit : str, default="1"
        Unit of measurement (dimensionless by default).

    Returns
    -------
    Counter
        An OpenTelemetry counter instrument.
    """
    return meter.create_counter(name=name, description=description, unit=unit)


def _create_up_down_counter(meter: Meter, name: str, description: str, unit: str = "1"):
    """
    Create an OpenTelemetry UpDownCounter instrument.

    Parameters
    ----------
    meter : Meter
        The OpenTelemetry meter used to create the counter.
    name : str
        The metric name (dot-delimited, e.g., "locust.user.count").
    description : str
        Human-readable description of the metric.
    unit : str, default="1"
        Unit of measurement (dimensionless by default).

    Returns
    -------
    UpDownCounter
        An OpenTelemetry up-down counter instrument.
    """
    return meter.create_up_down_counter(name=name, description=description, unit=unit)


class OtelLocustEvents:
    """
    Telemetry histograms for Locust test lifecycle events.

    Metrics provided
    ----------------
    - locust.test.start : Timestamp of test start events.
    - locust.test.stop : Timestamp of test stop events.
    - locust.test.spawn_complete : Timestamp of spawning completion.
    - locust.test.cpu_warning : CPU warning events with annotation.
    - locust.test.event : General test lifecycle events.
    """

    def __init__(self, meter: Meter):
        self.test_start_event = _create_histogram(
            meter, "locust.test.start", "Timestamp of test start events"
        )
        self.test_stop_event = _create_histogram(
            meter, "locust.test.stop", "Timestamp of test stop events"
        )
        self.spawn_complete_event = _create_histogram(
            meter, "locust.test.spawn_complete", "Timestamp of spawn complete events"
        )
        self.cpu_warning_event = _create_histogram(
            meter, "locust.test.cpu_warning", "CPU warning events with annotation"
        )
        self.test_event = _create_histogram(
            meter, "locust.test.event", "General test lifecycle events"
        )


class OtelRequestMetrics:
    """
    Telemetry counters and histograms for Locust request metrics.

    Metrics provided
    ----------------
    - locust.requests.count : Total number of requests made.
    - locust.requests.errors.count : Total number of failed requests.
    - locust.requests.endpoint.success.count : Successful requests by endpoint.
    - locust.requests.endpoint.errors.count : Errors by endpoint.
    - locust.requests.duration : Distribution of request response times (ms).
    - locust.requests.response_size : Distribution of response sizes (bytes).
    - locust.user.count : Current number of active virtual users.
    """

    def __init__(self, meter: Meter):
        self.requests_counter = _create_counter(
            meter, "locust.requests.count", "Total number of requests made"
        )
        self.errors_counter = _create_counter(
            meter, "locust.requests.errors.count", "Total number of failed requests"
        )
        self.endpoint_success_counter = _create_counter(
            meter,
            "locust.requests.endpoint.success.count",
            "Successful requests by endpoint",
        )
        self.endpoint_errors_counter = _create_counter(
            meter, "locust.requests.endpoint.errors.count", "Errors by endpoint"
        )
        self.request_duration = _create_histogram(
            meter, "locust.requests.duration", "Request response times"
        )
        self.response_size = _create_histogram(
            meter, "locust.requests.response_size", "Response sizes", unit="By"
        )
        self.user_count = _create_up_down_counter(
            meter, "locust.user.count", "Current number of active Virtual Users"
        )


class OtelSystemMetrics:
    """
    Telemetry histograms and counters for system-level metrics.

    Metrics provided
    ----------------
    - locust.cpu.usage : CPU usage percentage of the Locust runner process.
    - locust.memory.usage : Resident memory usage (RSS) in bytes.
    - locust.network.bytes_sent : Total bytes sent by the Locust process.
    - locust.network.bytes_received : Total bytes received by the Locust process.
    """

    def __init__(self, meter: Meter):
        # Replace observable gauges with histograms for CPU and memory
        self.cpu_usage = _create_histogram(
            meter, "locust.cpu.usage", "CPU usage percentage", "%"
        )
        self.memory_usage = _create_histogram(
            meter, "locust.memory.usage", "Memory usage (RSS)", "By"
        )
        self.network_bytes_sent = _create_counter(
            meter, "locust.network.bytes_sent", "Total bytes sent", "By"
        )
        self.network_bytes_received = _create_counter(
            meter, "locust.network.bytes_received", "Total bytes received", "By"
        )


class OtelMetricsDefinition:
    """
    Centralized registry of all Locust OpenTelemetry metrics.

    Responsibilities
    ----------------
    - Group metrics into three domains: events, requests, system.
    - Provide a single access point for all metric instruments.
    - Avoid global meter usage by requiring a specific Meter instance.
    """

    def __init__(self, meter: Meter):
        """
        Initialize all telemetry metrics using the provided OpenTelemetry Meter.

        Parameters
        ----------
        meter : Meter
            OpenTelemetry Meter instance for creating all metrics.
        """
        self.events = OtelLocustEvents(meter)
        self.requests = OtelRequestMetrics(meter)
        self.system = OtelSystemMetrics(meter)
