"""
JSON telemetry recorders for Locust.

This module defines master and worker recorder classes that integrate with
the Locust telemetry system and use JSON-specific handlers to capture and
log lifecycle events, system metrics, request metrics, and output.
"""

import logging

from locust_telemetry.core.recorder import (
    MasterNodeRecorder,
    WorkerNodeRecorder,
)

logger = logging.getLogger(__name__)


class LocustJsonMasterNodeRecorder(MasterNodeRecorder):
    """
    JSON-enabled telemetry recorder for the Locust master node.

    This class extends the base ``MasterNodeRecorder`` to provide
    JSON-based telemetry export. It sets up JSON-specific handlers for
    system metrics, request metrics, lifecycle events, and output handling.
    """


class LocustJsonWorkerNodeRecorder(WorkerNodeRecorder):
    """
    JSON-enabled telemetry recorder for Locust worker nodes.

    This class extends the base ``WorkerNodeRecorder`` to provide
    JSON-based telemetry export. It sets up JSON-specific handlers for
    system metrics, request metrics, lifecycle events, and output handling.
    """
