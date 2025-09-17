"""
OpenTelemetry recorders for Locust.

This module defines master and worker recorder classes that integrate with
the Locust telemetry system using OpenTelemetry (OTEL). These recorders
configure an OTLP exporter, register metric readers, and use OTEL-specific
handlers to capture and export lifecycle events, system metrics, request
metrics, and output.

Classes
-------
MasterLocustOtelRecorder
    Recorder for the Locust master node with OTEL metrics export.
WorkerLocustOtelRecorder
    Recorder for Locust worker nodes with OTEL metrics export.
"""

import logging

from locust.env import Environment

from locust_telemetry.common.clients import configure_otel
from locust_telemetry.core.recorder import (
    MasterTelemetryRecorder,
    WorkerTelemetryRecorder,
)
from locust_telemetry.recorders.otel.handlers import (
    OtelLifecycleHandler,
    OtelOutputHandler,
    OtelRequestHandler,
    OtelSystemMetricsHandler,
)

logger = logging.getLogger(__name__)


class MasterLocustOtelRecorder(MasterTelemetryRecorder):
    """
    OpenTelemetry-enabled telemetry recorder for the Locust master node.

    This class extends the base ``MasterTelemetryRecorder`` to add
    OpenTelemetry metric collection and export. It sets up OTEL-specific
    handlers for system metrics, request metrics, lifecycle events,
    and output handling. Additionally, it initializes the OTLP exporter
    and meter provider via ``configure_otel``.

    Parameters
    ----------
    env : locust.env.Environment
        The Locust environment object, providing runtime configuration
        and access to parsed options.

    Attributes
    ----------
    env : locust.env.Environment
        Reference to the Locust environment.
    """

    def __init__(self, env: Environment):
        """
        Initialize the master recorder with OTEL handlers
        and configure the OpenTelemetry exporter.

        Parameters
        ----------
        env : locust.env.Environment
            The Locust environment object.
        """
        super().__init__(
            env,
            output_handler_cls=OtelOutputHandler,
            lifecycle_handler_cls=OtelLifecycleHandler,
            system_handler_cls=OtelSystemMetricsHandler,
            requests_handler_cls=OtelRequestHandler,
        )
        configure_otel(self.env)


class WorkerLocustOtelRecorder(WorkerTelemetryRecorder):
    """
    OpenTelemetry-enabled telemetry recorder for Locust worker nodes.

    This class extends the base ``WorkerTelemetryRecorder`` to add
    OpenTelemetry metric collection and export. It sets up OTEL-specific
    handlers for system metrics, request metrics, lifecycle events,
    and output handling. Additionally, it initializes the OTLP exporter
    and meter provider via ``configure_otel``.

    Parameters
    ----------
    env : locust.env.Environment
        The Locust environment object, providing runtime configuration
        and access to parsed options.

    Attributes
    ----------
    env : locust.env.Environment
        Reference to the Locust environment.
    """

    def __init__(self, env: Environment):
        """
        Initialize the worker recorder with OTEL handlers
        and configure the OpenTelemetry exporter.

        Parameters
        ----------
        env : locust.env.Environment
            The Locust environment object.
        """
        super().__init__(
            env,
            output_handler_cls=OtelOutputHandler,
            lifecycle_handler_cls=OtelLifecycleHandler,
            system_handler_cls=OtelSystemMetricsHandler,
            requests_handler_cls=OtelRequestHandler,
        )
        configure_otel(self.env)
