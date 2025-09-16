"""
This module defines the telemetry mixin with all the event handler
that are common for both master and worker nodes.

Responsibilities
----------------
- Has all event handlers that are common for both master and worker
- Log CPU and memory usage in both master and worker
- Log any CPU warning in both master and worker
"""

import logging
from typing import Any, Optional

import gevent
import psutil
from locust.env import Environment

from locust_telemetry.common.telemetry import TelemetryData
from locust_telemetry.recorders.json.constants import LocustTestEvent

logger = logging.getLogger(__name__)


class LocustJsonTelemetryCommonRecorderMixin:
    """
    Event handler mixn that are common for both master and worker

    This recorder attaches to the ``cpu_warning`` event and also logs periodic
    system usage from both master and worker processes.
    """

    _system_metrics_logger: Optional[gevent.Greenlet] = None
    _process: psutil.Process = psutil.Process()

    def log_telemetry(self, telemetry: TelemetryData, **kwargs: Any) -> None:
        """
        Record structured telemetry data with environment context.

        Parameters
        ----------
        telemetry : TelemetryData
            The telemetry descriptor (event or metric)
        **kwargs : Any
            Additional attributes to include in the telemetry log
        """
        logger.info(
            f"Recording telemetry: {telemetry.name}",
            extra={
                "telemetry": {
                    "telemetry_type": telemetry.type,
                    "telemetry_name": telemetry.name,
                    **self.recorder_context(),
                    **kwargs,
                }
            },
        )

    def on_cpu_warning(
        self,
        environment: Environment,
        cpu_usage: float,
        message: Optional[str] = None,
        timestamp: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """
        Handle the cpu_warning event.

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        cpu_usage : float
            CPU usage percentage.
        message : Optional[str], optional
            Optional message describing the warning.
        timestamp : Optional[float], optional
            Unix timestamp of the warning.
        **kwargs : Any
            Additional keyword arguments from Locust events.
        """
        self.log_telemetry(
            telemetry=LocustTestEvent.CPU_WARNING.value,
            cpu_usage=cpu_usage,
            message=message or "high_cpu_utilization",
            severity="warning",
        )

    def record_current_system_metrics(self):
        """
        Periodic tasks that fetches the locust runners usage and logs it to the console.
        This metrics can be used to observe if there are any bottlenecks with the
        runner / nodes. Useful for the large tests

        Note: Locust already have usage_monitor event, however it fires every 10
        seconds and cannot be configured. Hence, this method allows us to monitor system
        usage according to our convenience.
        """
        try:
            cpu_usage = self._process.cpu_percent()
            # Convert from bytes to Mebibytes
            memory_usage = self._process.memory_info().rss / (1024 * 1024)
            self.log_telemetry(
                telemetry=LocustTestEvent.USAGE.value,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
            )
        except psutil.Error as e:
            logger.warning(f"[json] psutil error during metric collection: {e}")

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        Fire CPU warning and memory usage metrics only during tests

        On test start initialise event listener
            - cpu_warning
            - usage_monitor
        """
        self.env.events.cpu_warning.add_listener(self.on_cpu_warning)
        self._system_metrics_logger = gevent.spawn(self._start_recording_system_metrics)

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Remove CPU warning and memory usage event listener when test is stopped

        On test stop remove event listener handlers
            - cpu_warning
            - usage_monitor
        """
        self.env.events.cpu_warning.remove_listener(self.on_cpu_warning)
        self._stop_recording_system_metrics()

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
        try:
            while True:
                self.record_current_system_metrics()
                gevent.sleep(collection_interval)
        except gevent.GreenletExit:
            logger.info("[json] System metrics collection terminated gracefully")
        except Exception:
            logger.exception("[json] System metrics collection loop failed")

    def _stop_recording_system_metrics(self) -> None:
        """
        Terminate the system metrics recorder gevent
        """
        if self._system_metrics_logger is None:
            return

        self._system_metrics_logger.kill()
        self._system_metrics_logger = None
        logger.debug("[json] System metrics collection process terminated")
