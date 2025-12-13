"""
OpenTelemetry recorders for Locust.

This module defines master and worker recorder classes that integrate with
the Locust telemetry system using OpenTelemetry (OTEL). These recorders
configure an OTLP exporter, register metric readers, and use OTEL-specific
handlers to capture and export lifecycle events, system metrics, request
metrics, and output.
"""

import logging

from locust_telemetry.core.recorder import (
    MasterNodeRecorder,
    WorkerNodeRecorder,
)

logger = logging.getLogger(__name__)


class LocustOtelMasterNodeRecorder(MasterNodeRecorder):
    """
    OpenTelemetry-enabled telemetry recorder for the Locust master node.

    This class extends the base :class:`MasterNodeRecorder` to add
    OpenTelemetry metric collection and export. It sets up OTEL-specific
    handlers for system metrics, request metrics, lifecycle events,
    and output handling. Additionally, it initializes the OTLP exporter
    and meter provider via :func:`configure_otel`.

    Notes
    -----
    Currently, this class does not override any methods, but it exists
    as a specialization hook for future master-specific behavior.
    """


class LocustOtelWorkerNodeRecorder(WorkerNodeRecorder):
    """
    OpenTelemetry-enabled telemetry recorder for Locust worker nodes.

    This class extends the base :class:`WorkerNodeRecorder` to add
    OpenTelemetry metric collection and export. It sets up OTEL-specific
    handlers for system metrics, request metrics, lifecycle events,
    and output handling. Additionally, it initializes the OTLP exporter
    and meter provider via :func:`configure_otel`.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the worker recorder and attach request listeners.

        Parameters
        ----------
        *args : Any
            Positional arguments passed to the base class initializer.
        **kwargs : Any
            Keyword arguments passed to the base class initializer.
        """
        super().__init__(*args, **kwargs)
        self.env.events.request.add_listener(self.on_request)

    def on_request(self, *args, **kwargs):
        """
        Handle a request event from Locust and record it as a histogram.

        This method is registered as an event listener on
        :attr:`env.events.request`.

        Parameters
        ----------
        *args : Any
            Positional arguments forwarded from the Locust request event.
        **kwargs : Any
            Keyword arguments forwarded from the Locust request event,
            typically including ``name``, ``response_time``, and
            ``exception`` fields.
        """
        self.requests.on_request(*args, **kwargs)
