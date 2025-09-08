"""
This module provides the `WorkerLocustTelemetryRecorder` class, which runs on
Locust worker nodes. It captures worker-specific telemetry such as CPU warnings
and logs them in a format suitable for observability tools.

Responsibilities
----------------
- Listen to worker-specific events: `cpu_warning`.
- Provide extension points for additional worker-level telemetry.
"""

import logging
import os
import socket
from typing import Any, ClassVar, Optional

from locust.env import Environment

from locust_telemetry.core.telemetry import BaseTelemetryRecorder
from locust_telemetry.core_telemetry.constants import LocustTestEvent

logger = logging.getLogger(__name__)


class WorkerLocustTelemetryRecorder(BaseTelemetryRecorder):
    """
    Telemetry recorder for Locust worker nodes.

    Responsibilities
    ----------------
    - Handle worker-specific telemetry, such as CPU warnings.
    - Provide extension points for additional worker-level telemetry.

    Attributes
    ----------
    name : ClassVar[str]
        Identifier for the recorder.
    """

    name: ClassVar[str] = "worker_locust_telemetry_recorder"

    def __init__(self, env: Environment) -> None:
        """
        Initialize the worker telemetry recorder.

        Registers event listeners for worker-specific events.

        Parameters
        ----------
        env : Environment
            The Locust environment instance.
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
            message=message,
            text=(
                f"{self.env.parsed_options.testplan} high CPU usage "
                f"({cpu_usage:.2f}%)"
            ),
        )
