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
from locust.runners import MasterRunner

from locust_telemetry.recorders.json.locust.constants import LocustTestEvent

logger = logging.getLogger(__name__)


class LocustJsonTelemetryCommonRecorderMixin:
    """
    Event handler mixn that are common for both master and worker

    This recorder attaches to the ``cpu_warning`` event and also logs periodic
    system usage from both master and worker processes.
    """

    _usage_monitor_logger = None

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
            source_type=environment.runner.__class__.__name__,
            source_id=(
                "master"
                if isinstance(self.env.runner, MasterRunner)
                else f"worker-{self.env.runner.worker_index}"
            ),
            cpu_usage=cpu_usage,
            message=message,
            text=(
                f"{self.env.parsed_options.testplan} high CPU usage "
                f"({cpu_usage:.2f}%)"
            ),
        )

    def _log_usage_monitor(self):
        """
        Periodic tasks that fetches the locust runners usage and logs it to the console.
        This metrics can be used to observe if there are any bottlenecks with the
        runner / nodes. Useful for the large tests

        Note: Locust already have usage_monitor event, however it fires every 10
        seconds and cannot be configured. Hence, this method allows us to monitor system
        usage according to our convenience.

        """
        process = psutil.Process()
        while True:
            cpu_usage = process.cpu_percent()
            # Convert from bytes to Mebibytes
            memory_usage = process.memory_info().rss / 1024 / 1024
            self.log_telemetry(
                telemetry=LocustTestEvent.USAGE.value,
                source_type=self.env.runner.__class__.__name__,
                source_id=(
                    "master"
                    if isinstance(self.env.runner, MasterRunner)
                    else f"worker-{self.env.runner.worker_index}"
                ),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
            )
            gevent.sleep(self.env.parsed_options.lt_system_usage_recorder_interval)

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        Fire CPU warning and memory usage metrics only during tests

        On test start initialise event listener
            - cpu_warning
            - usage_monitor
        """
        self.env.events.cpu_warning.add_listener(self.on_cpu_warning)
        self._usage_monitor_logger = gevent.spawn(self._log_usage_monitor)

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Remove CPU warning and memory usage event listener when test is stopped

        On test stop remove event listener handlers
            - cpu_warning
            - usage_monitor
        """
        self.env.events.cpu_warning.remove_listener(self.on_cpu_warning)
        if self._usage_monitor_logger is not None:
            self._usage_monitor_logger.kill()
            self._usage_monitor_logger = None
