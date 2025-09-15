"""
OpenTelemetry system metrics mixin for Locust telemetry recorders.

Provides reusable system-level metric collection capabilities for both master and worker
nodes in distributed Locust deployments. Handles CPU, memory, and network metric
collection along with system event monitoring.
"""

import logging
from typing import Any, Dict, Optional

import gevent
import psutil
from locust.env import Environment

from locust_telemetry.common.clients import configure_otel
from locust_telemetry.recorders.otel.metrics import OtelMetricsDefinition

logger = logging.getLogger(__name__)


class LocustOtelCommonRecorderMixin:
    """
    Mixin class providing system-level OpenTelemetry metric collection capabilities.

    Encapsulates common telemetry functionality for both master and worker nodes,
    including system resource monitoring, event handling, and metric export.

    Responsibilities
    ----------------
    - System resource monitoring (CPU, memory, network I/O)
    - CPU warning event handling and telemetry
    - Background metric collection process management
    - OpenTelemetry meter configuration and initialization

    Interface Requirements
    ---------------------
    Subclasses must implement:
    - recorder_context(): Returns context attributes for metric enrichment
    - now_ms: Property providing current timestamp in milliseconds

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

        Parameters
        ----------
        environment : Environment
            Locust environment instance for configuration context
        **kwargs : Any
            Additional configuration parameters passed from init event

        Notes
        -----
        This method is automatically invoked during Locust environment initialization
        via event listener registration.
        """
        meter = configure_otel(environment)
        self.metrics: OtelMetricsDefinition = OtelMetricsDefinition(meter)
        logger.debug("[otel] OpenTelemetry meter configured successfully")

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize system metric collection upon test commencement.

        Establishes background monitoring processes and registers event listeners
        for comprehensive system telemetry collection.

        Notes
        -----
        Subclasses should invoke super().on_test_start() when overriding this method
        to ensure proper system metric collection initialization.
        """
        logger.info("[otel] Initializing system metrics collection")

        # Register CPU warning event listener
        self.env.events.cpu_warning.add_listener(self.on_cpu_warning)

        # Launch background system metrics collection
        self._system_metrics_recorder = gevent.spawn(
            self._start_recording_system_metrics
        )

        logger.info("[otel] System metrics collection initialized successfully")

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Terminate system metric collection processes upon test completion.

        Ensures clean shutdown of background collectors and proper cleanup
        of event listeners and resources.

        Notes
        -----
        Subclasses should invoke super().on_test_stop() when overriding this method
        to ensure proper system metric collection termination.
        """
        logger.info("[otel] Terminating system metrics collection")

        # Remove event listeners
        self.env.events.cpu_warning.remove_listener(self.on_cpu_warning)

        self._stop_recording_system_metrics()

    def on_cpu_warning(
        self,
        environment: Environment,
        cpu_usage: float,
        message: Optional[str] = None,
        timestamp: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """
        Process CPU warning events and record corresponding telemetry.

        Parameters
        ----------
        environment : Environment
            Locust environment instance generating the warning
        cpu_usage : float
            CPU utilization percentage at warning time
        message : Optional[str], optional
            Descriptive message providing warning context
        timestamp : Optional[float], optional
            Event timestamp in seconds since epoch
        **kwargs : Any
            Additional event parameters
        """
        warning_attributes = {
            **self.recorder_context(),
            "cpu_usage": f"{cpu_usage:.1f}",
            "message": message or "high_cpu_utilization",
            "severity": "warning",
        }
        self.metrics.events.cpu_warning_event.record(
            self.now_ms, attributes=warning_attributes
        )
        logger.warning(
            f"[otel] CPU warning recorded: {cpu_usage}% - {message}",
            extra=warning_attributes,
        )

    def _start_recording_system_metrics(self) -> None:
        """
        Background process for periodic system metric collection.

        Continuously monitors and records system resource utilization metrics
        at configured intervals until explicitly terminated.

        Notes
        -----
        Execution interval controlled by lt_stats_recorder_interval environment option.
        Implements graceful error handling to ensure continuous operation.
        """
        logger.info("Starting system metrics collection loop")
        collection_interval = self.env.parsed_options.lt_stats_recorder_interval
        context = self.recorder_context()
        try:
            while True:
                self.record_current_system_metrics(context)
                gevent.sleep(collection_interval)
        except gevent.GreenletExit:
            logger.info("[otel] System metrics collection terminated gracefully")
        except Exception:
            logger.exception("[otel] System metrics collection loop failed")

    def _stop_recording_system_metrics(self) -> None:
        """
        Terminate the system metrics recorder gevent
        """
        if self._system_metrics_recorder is None:
            return

        self._system_metrics_recorder.kill()
        self._system_metrics_recorder = None
        logger.debug("[otel] System metrics collection process terminated")

    def record_current_system_metrics(self, context: Dict[str, str]) -> None:
        """
        Collect and record current system resource utilization metrics.

        Parameters
        ----------
        context : Dict[str, str]
            Context attributes for metric enrichment

        Records CPU utilization, memory consumption, and network I/O metrics
        with appropriate timestamps and contextual metadata.
        """
        current_time = self.now_ms
        metric_attributes = {**context, "unit": "percent"}

        try:
            # CPU Utilization
            cpu_usage = self._process.cpu_percent()
            self.metrics.system.cpu_usage.record(
                current_time,
                attributes={**metric_attributes, "value": cpu_usage},
            )

            # Memory Consumption (MiB)
            memory_mib = self._process.memory_info().rss / (1024 * 1024)
            self.metrics.system.memory_usage.record(
                current_time,
                attributes={
                    **context,
                    "value": memory_mib,
                    "unit": "mebibytes",
                },
            )

            # Network I/O (cumulative bytes)
            current_io = psutil.net_io_counters()
            self.metrics.system.network_bytes_sent.record(
                current_time,
                attributes={
                    **context,
                    "value": str(current_io.bytes_sent),
                    "unit": "bytes",
                },
            )
            self.metrics.system.network_bytes_received.record(
                current_time,
                attributes={
                    **context,
                    "value": str(current_io.bytes_recv),
                    "unit": "bytes",
                },
            )

        except psutil.Error as e:
            logger.warning(f"[otel] psutil error during metric collection: {e}")
