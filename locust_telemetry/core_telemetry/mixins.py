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

from locust.env import Environment
from locust.runners import MasterRunner

from locust_telemetry.core_telemetry.constants import LocustTestEvent

logger = logging.getLogger(__name__)


class LocustTelemetryCommonRecorderMixin:
    """
    Event handler mixn that are common for both master and worker

    This recorder attaches to the ``usage_monitor`` event and logs periodic
    CPU and memory usage from both master and worker processes.
    """

    def on_usage_monitor(
        self, environment: Environment, cpu_usage: float, memory_usage: int
    ):
        """
        Event handler for ``usage_monitor`` events.

        Logs periodic system usage metrics (CPU and memory) from either master
        or worker nodes. Memory usage is automatically converted from bytes to
        Mebibytes (MiB).

        :param environment: The current Locust environment.
        :type environment: Environment
        :param cpu_usage: CPU usage percentage reported by Locust.
        :type cpu_usage: float
        :param memory_usage: Memory usage in bytes (will be converted to MiB).
        :type memory_usage: int
        """
        # Convert from bytes to Mebibytes
        memory_usage = memory_usage / 1024 / 1024
        self.log_telemetry(
            telemetry=LocustTestEvent.USAGE.value,
            source_type=environment.runner.__class__.__name__,
            source_id=(
                "master"
                if isinstance(self.env.runner, MasterRunner)
                else f"worker-{self.env.runner.worker_index}"
            ),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
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

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        Fire CPU warning and memory usage metrics only during tests

        On test start initialise event listener
            - cpu_warning
            - usage_monitor
        """
        self.env.events.cpu_warning.add_listener(self.on_cpu_warning)
        self.env.events.usage_monitor.add_listener(self.on_usage_monitor)

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Remove CPU warning and memory usage event listener when test is stopped

        On test stop remove event listener handlers
            - cpu_warning
            - usage_monitor
        """
        self.env.events.cpu_warning.remove_listener(self.on_cpu_warning)
        self.env.events.usage_monitor.remove_listener(self.on_usage_monitor)
