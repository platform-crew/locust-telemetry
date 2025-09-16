import logging
from typing import ClassVar, Optional

from locust.env import Environment

from locust_telemetry.core.recorder import TelemetryBaseRecorder
from locust_telemetry.recorders.otel.metrics import OtelMetricsDefinition
from locust_telemetry.recorders.otel.mixins import LocustOtelCommonRecorderMixin

logger = logging.getLogger(__name__)


class WorkerLocustOtelRecorder(TelemetryBaseRecorder, LocustOtelCommonRecorderMixin):
    """
    OpenTelemetry recorder for Locust worker nodes.

    Collects system and request-level telemetry, including request durations
    and associated attributes. Integrates with Locust test lifecycle events
    to start/stop metrics collection appropriately.

    Inherits
    --------
    TelemetryBaseRecorder : Base recorder interface for Locust telemetry.
    LocustOtelCommonRecorderMixin : Provides system metrics (CPU, memory, network).

    Attributes
    ----------
    name : ClassVar[str]
        Unique identifier for this recorder type.
    metrics : Optional[OtelMetricsDefinition]
        Container for all OpenTelemetry metrics instruments (gauges, histograms).
    """

    name: ClassVar[str] = "worker_otel_recorder"

    def __init__(self, env: Environment) -> None:
        """
        Initialize the Worker OpenTelemetry recorder.

        Sets up OpenTelemetry configuration, initializes metrics container,
        and registers event listeners for test lifecycle and request events.

        Parameters
        ----------
        env : Environment
            Locust environment instance providing access to test state
            and event hooks.
        """
        super().__init__(env)

        self.metrics: Optional[OtelMetricsDefinition] = None

        # Configure OpenTelemetry meter when environment initializes
        env.events.init.add_listener(self.configure_otel)

        # Register worker-specific event listeners
        self.env.events.test_start.add_listener(self.on_test_start)
        self.env.events.test_stop.add_listener(self.on_test_stop)
        self.env.events.request.add_listener(self.on_request)

    def on_request(self, *args, **kwargs) -> None:
        """
        Handle request completion events and record request metrics.

        Records request duration along with endpoint, HTTP method, and exception
        information for observability.

        Parameters
        ----------
        *args : Any
            Positional arguments from the Locust request event.
        **kwargs : Any
            Keyword arguments from the Locust request event, expected keys:
            - name : str
                Endpoint name or route.
            - request_type : str
                HTTP method (GET, POST, etc.).
            - response_time : float
                Duration of the request in milliseconds.
            - exception : Optional[Exception]
                Exception object if the request failed; None otherwise.
        """
        attributes = self.recorder_context()
        attributes.update(
            {
                "endpoint": kwargs.get("name"),
                "http_method": kwargs.get("request_type"),
                "exception": bool(kwargs.get("exception")),
            }
        )

        self.metrics.requests.request_duration.record(
            kwargs.get("response_time"), attributes=attributes
        )
