"""
This module provides the `WorkerLocustOtelRecorder` class, which runs on
Locust worker nodes. It captures worker-specific telemetry such as CPU warnings,
System usage, network usage and records them in a otel format suitable
for observability tools.

Responsibilities
----------------
- Listen to worker-specific events: `cpu_warning`, `system_usage`, `network_usage`.
- Provide extension points for additional worker-level telemetry.
"""

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

    Responsibilities
    ----------------
    - Handle worker-specific telemetry, such as CPU warnings.
    - Provide extension points for additional worker-level telemetry.

    Attributes
    ----------
    name : ClassVar[str]
        Identifier for the recorder.
    """

    name: ClassVar[str] = "worker_otel_recorder"

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

        # Configure otel
        # This will be set by configure otel
        self.metrics: Optional[OtelMetricsDefinition] = None
        env.events.init.add_listener(self.configure_otel)

        # Register master-only event listeners
        self.env.events.test_start.add_listener(self.on_test_start)
        self.env.events.test_stop.add_listener(self.on_test_stop)
