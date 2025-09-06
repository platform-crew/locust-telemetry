"""
Worker Node Stats Recorder

This module provides the `WorkerNodeStatsRecorder` class, which runs on
Locust worker nodes. It captures worker-specific metrics such as CPU warnings and
logs them for observability tools.

The recorder listens to:
- cpu_warning

It can be extended to capture additional worker-level metrics.
"""

import logging
import os
import socket
from typing import Any, ClassVar, Optional

from locust.env import Environment

from locust_observability.metrics import EventsEnum
from locust_observability.recorders.base import BaseRecorder

logger = logging.getLogger(__name__)


class WorkerNodeStatsRecorder(BaseRecorder):
    """
    Recorder for Locust worker nodes.

    This recorder captures:
    - Worker-specific metrics, such as CPU warnings.
    - Additional metrics can be added in the future.

    Attributes:
        name (ClassVar[str]): Identifier for the recorder.
    """

    name: ClassVar[str] = "worker_recorder"

    def __init__(self, env: Environment) -> None:
        """
        Initialize the worker node stats recorder.

        Args:
            env (Environment): The Locust environment instance.
        """
        super().__init__(env)
        self._hostname: str = socket.gethostname()
        self._pid: int = os.getpid()

        # Register worker-specific event listeners
        env.events.cpu_warning.add_listener(self.on_cpu_warning)

    # --- Event Handlers ---

    def on_cpu_warning(
        self,
        environment: Environment,
        cpu_usage: float,
        message: Optional[str] = None,
        timestamp: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """
        Handler called when high CPU usage is detected.

        Args:
            environment (Environment): The Locust environment instance.
            cpu_usage (float): CPU usage percentage.
            message (Optional[str]): Optional message describing the warning.
            timestamp (Optional[float]): Unix timestamp of the warning.
            **kwargs: Additional keyword arguments from Locust events.
        """
        self.log_metrics(
            metric=EventsEnum.CPU_WARNING_EVENT.value,
            cpu_usage=cpu_usage,
            message=message,
            text=(
                f"{self.env.parsed_options.testplan} High CPU usage "
                f"({cpu_usage:.2f}%)"
            ),
        )
