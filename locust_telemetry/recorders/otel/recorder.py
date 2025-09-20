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

logger = logging.getLogger(__name__)


class BaseOtelRecorder:
    """
    Base class to initialize OpenTelemetry configuration.

    Ensures that the OTLP exporter, meter provider, and metric readers
    are configured before any Locust telemetry handlers are registered.

    This class should be inherited alongside MasterTelemetryRecorder
    or WorkerTelemetryRecorder.
    """

    def __init__(self, env: Environment):
        configure_otel(env)


class MasterLocustOtelRecorder(BaseOtelRecorder, MasterTelemetryRecorder):
    """
    OpenTelemetry-enabled telemetry recorder for the Locust master node.

    This class extends the base ``MasterTelemetryRecorder`` to add
    OpenTelemetry metric collection and export. It sets up OTEL-specific
    handlers for system metrics, request metrics, lifecycle events,
    and output handling. Additionally, it initializes the OTLP exporter
    and meter provider via ``configure_otel``.
    """

    def __init__(self, *args, **kwargs):
        BaseOtelRecorder.__init__(self, env=kwargs.get("env"))
        MasterTelemetryRecorder.__init__(self, *args, **kwargs)


class WorkerLocustOtelRecorder(BaseOtelRecorder, WorkerTelemetryRecorder):
    """
    OpenTelemetry-enabled telemetry recorder for Locust worker nodes.

    This class extends the base ``WorkerTelemetryRecorder`` to add
    OpenTelemetry metric collection and export. It sets up OTEL-specific
    handlers for system metrics, request metrics, lifecycle events,
    and output handling. Additionally, it initializes the OTLP exporter
    and meter provider via ``configure_otel``.
    """

    def __init__(self, *args, **kwargs):
        BaseOtelRecorder.__init__(self, env=kwargs.get("env"))
        WorkerTelemetryRecorder.__init__(self, *args, **kwargs)
        self.env.events.request.add_listener(self.on_request)

    def on_request(self, *args, **kwargs):
        """On request, record it as a histogram"""
        self.requests.on_request(*args, **kwargs)
