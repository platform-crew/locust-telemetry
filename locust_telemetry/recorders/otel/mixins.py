"""
OpenTelemetry system metrics mixin for Locust telemetry recorders.

Provides reusable system-level metric collection capabilities for both master
and worker nodes in distributed Locust deployments. Handles CPU, memory, and
network metric collection along with system event monitoring.
"""

import logging
from typing import Any, Optional

import gevent
import psutil
from locust.env import Environment

from locust_telemetry.common.clients import configure_otel
from locust_telemetry.recorders.otel.metrics import OtelMetricsDefinition

logger = logging.getLogger(__name__)


class LocustOtelCommonRecorderMixin:
    """
    Mixin providing system-level OpenTelemetry metric collection for Locust.

    Encapsulates common telemetry functionality for both master and worker nodes,
    including system resource monitoring, event handling, and metric export.

    Responsibilities
    ----------------
    - Monitor system resources (CPU, memory, network I/O)
    - Handle CPU warning events and record telemetry
    - Manage background metric collection
    - Configure and initialize OpenTelemetry meters and instruments

    Required Subclass Interface
    ---------------------------
    Subclasses must implement:
    - recorder_context() -> Dict[str, str]: Returns metric context attributes
    - now_ms (property) -> int: Current timestamp in milliseconds

    Usage
    -----
    class MyRecorder(LocustOtelCommonRecorderMixin, TelemetryBaseRecorder):
        def recorder_context(self) -> Dict[str, str]:
            return {"run_id": self.env.run_id, "testplan": self.testplan_name}

        @property
        def now_ms(self) -> int:
            return int(time.time() * 1000)
    """

    _system_metrics_recorder: Optional[gevent.Greenlet] = None
    _process: psutil.Process = psutil.Process()

    def configure_otel(self, environment: Environment, **kwargs: Any) -> None:
        """
        Initialize OpenTelemetry meter and metric instruments.

        Configures OTLP exporter, attaches a periodic metrics reader, and
        registers system and request-level gauges.

        Parameters
        ----------
        environment : Environment
            Locust environment instance providing configuration and context.
        **kwargs : Any
            Additional configuration options (currently unused).

        Notes
        -----
        Should be called during Locust environment initialization. Sets up
        `self.metrics` containing all observable gauges and histograms.
        """
        configure_otel(environment)
        self.metrics = OtelMetricsDefinition(self)
        logger.debug("[otel] OpenTelemetry meter configured successfully")

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        Start system metric collection when the test begins.

        Registers event listeners and prepares background monitoring processes.

        Notes
        -----
        Subclasses overriding this method should call
        `super().on_test_start()` to ensure proper initialization.
        """
        logger.info("[otel] Initializing system metrics collection")

        # Register CPU warning listener
        self.env.events.cpu_warning.add_listener(self.on_cpu_warning)

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Stop system metric collection when the test ends.

        Cleans up background collectors and removes event listeners.

        Notes
        -----
        Subclasses overriding this method should call
        `super().on_test_stop()` to ensure proper termination.
        """
        logger.info("[otel] Terminating system metrics collection")

        # Remove CPU warning listener
        self.env.events.cpu_warning.remove_listener(self.on_cpu_warning)

    def on_cpu_warning(
        self,
        environment: Environment,
        cpu_usage: float,
        message: Optional[str] = None,
        timestamp: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """
        Record a CPU warning event in OpenTelemetry.

        Parameters
        ----------
        environment : Environment
            Locust environment instance generating the warning.
        cpu_usage : float
            CPU utilization percentage at the time of the warning.
        message : Optional[str], default=None
            Optional descriptive message for the warning.
        timestamp : Optional[float], default=None
            Event timestamp in seconds since epoch.
        **kwargs : Any
            Additional metadata to attach to the event.

        Notes
        -----
        This method records the event via `self.metrics.events.test_event`
        and logs a warning with context attributes.
        """
        self.metrics.events.test_event.record(
            self.now_ms,
            attributes=self.recorder_context(
                severity="warning",
                message=message or "high_cpu_utilization",
                cpu_usage=cpu_usage,
            ),
        )
        logger.warning(
            f"[otel] CPU warning recorded: {cpu_usage}% - {message}",
            extra=self.recorder_context(),
        )
