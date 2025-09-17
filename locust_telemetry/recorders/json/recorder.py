"""
JSON telemetry recorders for Locust.

This module defines master and worker recorder classes that integrate with
the Locust telemetry system and use JSON-specific handlers to capture and
log lifecycle events, system metrics, request metrics, and output.

Classes
-------
MasterLocustJsonTelemetryRecorder
    Recorder for the Locust master node with metrics as json logs.
WorkerLocustJsonTelemetryRecorder
    Recorder for Locust worker nodes with metrics as json logs.
"""

import logging

from locust.env import Environment

from locust_telemetry.core.recorder import (
    MasterTelemetryRecorder,
    WorkerTelemetryRecorder,
)
from locust_telemetry.recorders.json.handlers import (
    JsonTelemetryLifecycleHandler,
    JsonTelemetryOutputHandler,
    JsonTelemetryRequestHandler,
    JsonTelemetrySystemMetricsHandler,
)

logger = logging.getLogger(__name__)


class MasterLocustJsonTelemetryRecorder(MasterTelemetryRecorder):
    """
    JSON-enabled telemetry recorder for the Locust master node.

    This class extends the base ``MasterTelemetryRecorder`` to provide
    JSON-based telemetry export. It sets up JSON-specific handlers for
    system metrics, request metrics, lifecycle events, and output handling.

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
        Initialize the master recorder with JSON telemetry handlers.

        Parameters
        ----------
        env : locust.env.Environment
            The Locust environment object.
        """
        super().__init__(
            env,
            output_handler_cls=JsonTelemetryOutputHandler,
            lifecycle_handler_cls=JsonTelemetryLifecycleHandler,
            system_handler_cls=JsonTelemetrySystemMetricsHandler,
            requests_handler_cls=JsonTelemetryRequestHandler,
        )


class WorkerLocustJsonTelemetryRecorder(WorkerTelemetryRecorder):
    """
    JSON-enabled telemetry recorder for Locust worker nodes.

    This class extends the base ``WorkerTelemetryRecorder`` to provide
    JSON-based telemetry export. It sets up JSON-specific handlers for
    system metrics, request metrics, lifecycle events, and output handling.

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
        Initialize the worker recorder with JSON telemetry handlers.

        Parameters
        ----------
        env : locust.env.Environment
            The Locust environment object.
        """
        super().__init__(
            env,
            output_handler_cls=JsonTelemetryOutputHandler,
            lifecycle_handler_cls=JsonTelemetryLifecycleHandler,
            system_handler_cls=JsonTelemetrySystemMetricsHandler,
            requests_handler_cls=JsonTelemetryRequestHandler,
        )
