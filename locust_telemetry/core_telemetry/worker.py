"""
This module provides the `WorkerLocustTelemetryRecorder` class, which runs on
Locust worker nodes. It captures worker-specific telemetry such as CPU warnings,
System usage and logs them in a format suitable for observability tools.

Responsibilities
----------------
- Listen to worker-specific events: `cpu_warning`, `system_usage`.
- Provide extension points for additional worker-level telemetry.
"""

import logging
from typing import ClassVar

from locust.env import Environment

from locust_telemetry.core.recorder import BaseTelemetryRecorder
from locust_telemetry.core_telemetry.mixins import LocustTelemetryCommonRecorderMixin

logger = logging.getLogger(__name__)


class WorkerLocustTelemetryRecorder(
    BaseTelemetryRecorder, LocustTelemetryCommonRecorderMixin
):
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

        Registers event listeners for test lifecycle events.

        Parameters
        ----------
        env : Environment
            The Locust environment instance.
        """
        super().__init__(env)

        # Register master-only event listeners
        self.env.events.test_start.add_listener(self.on_test_start)
        self.env.events.test_stop.add_listener(self.on_test_stop)
