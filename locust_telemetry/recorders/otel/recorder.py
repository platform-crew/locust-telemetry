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
from typing import Any

from locust_telemetry.common.clients import configure_otel
from locust_telemetry.core.recorder import (
    MasterTelemetryRecorder,
    WorkerTelemetryRecorder,
)

logger = logging.getLogger(__name__)


class LocustOtelRecorderMixin:

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        On test start configure otel and call the base
        """
        logger.info("[otel] Configuring otel on test start")
        configure_otel(self.env)
        super().on_test_start(*args, **kwargs)

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Lifecycle hook for test stop.
        De-registers metrics and shuts down the OpenTelemetry provider.
        """
        super().on_test_stop(*args, **kwargs)
        provider = getattr(self.env, "otel_provider", None)
        if not provider:
            logger.warning("[otel] Otel metric provider never configured")
            return

        try:
            provider.shutdown()
            logger.info("[otel] Otel provider shutdown successfully")
        except Exception:
            logger.exception("[otel] Otel provider failed to shutdown")
            raise
        finally:
            del self.env.otel_provider


class MasterLocustOtelRecorder(LocustOtelRecorderMixin, MasterTelemetryRecorder):
    """
    OpenTelemetry-enabled telemetry recorder for the Locust master node.

    This class extends the base ``MasterTelemetryRecorder`` to add
    OpenTelemetry metric collection and export. It sets up OTEL-specific
    handlers for system metrics, request metrics, lifecycle events,
    and output handling. Additionally, it initializes the OTLP exporter
    and meter provider via ``configure_otel``.
    """

    pass


class WorkerLocustOtelRecorder(LocustOtelRecorderMixin, WorkerTelemetryRecorder):
    """
    OpenTelemetry-enabled telemetry recorder for Locust worker nodes.

    This class extends the base ``WorkerTelemetryRecorder`` to add
    OpenTelemetry metric collection and export. It sets up OTEL-specific
    handlers for system metrics, request metrics, lifecycle events,
    and output handling. Additionally, it initializes the OTLP exporter
    and meter provider via ``configure_otel``.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.env.events.request.add_listener(self.on_request)

    def on_request(self, *args, **kwargs):
        """On request, record it as a histogram"""
        self.requests.on_request(*args, **kwargs)
