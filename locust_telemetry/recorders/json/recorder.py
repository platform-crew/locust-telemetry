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

from locust_telemetry.core.recorder import (
    MasterTelemetryRecorder,
    WorkerTelemetryRecorder,
)

logger = logging.getLogger(__name__)


class MasterLocustJsonTelemetryRecorder(MasterTelemetryRecorder):
    """
    JSON-enabled telemetry recorder for the Locust master node.

    This class extends the base ``MasterTelemetryRecorder`` to provide
    JSON-based telemetry export. It sets up JSON-specific handlers for
    system metrics, request metrics, lifecycle events, and output handling.
    """

    pass


class WorkerLocustJsonTelemetryRecorder(WorkerTelemetryRecorder):
    """
    JSON-enabled telemetry recorder for Locust worker nodes.

    This class extends the base ``WorkerTelemetryRecorder`` to provide
    JSON-based telemetry export. It sets up JSON-specific handlers for
    system metrics, request metrics, lifecycle events, and output handling.
    """

    pass
