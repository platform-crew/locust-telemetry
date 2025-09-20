"""
OpenTelemetry handlers for Locust.

This module provides handler implementations for lifecycle events, system
metrics, request metrics, and output in the context of OpenTelemetry.
These handlers are used by the OTEL recorders for both master and worker
nodes to collect and export telemetry data to an OTLP endpoint.

Classes
-------
OtelLifecycleHandler
    Registers and records lifecycle event metrics (e.g., test start/stop,
    user counts).
OtelOutputHandler
    Central registry for OTEL instruments; manages recording of events
    and request metrics.
OtelRequestHandler
    Registers request-related metrics (success/error histograms) and
    records request durations.
OtelSystemMetricsHandler
    Registers and reports system-level metrics (CPU, memory, network I/O)
    via observable callbacks.
"""

import logging
from typing import Any, List

import psutil
from locust.env import Environment
from opentelemetry.metrics import Observation

from locust_telemetry.common import helpers as h
from locust_telemetry.core.events import TelemetryEventsEnum, TelemetryMetricsEnum
from locust_telemetry.core.handlers import (
    BaseLifecycleHandler,
    BaseOutputHandler,
    BaseRequestHandler,
    BaseSystemMetricsHandler,
)
from locust_telemetry.recorders.otel.exceptions import OtelMetricNotRegisteredError

logger = logging.getLogger(__name__)


class OtelOutputHandler(BaseOutputHandler):
    """
    OpenTelemetry output handler.

    Responsible for recording lifecycle events and metrics using registered
    OTEL instruments.
    """

    def __init__(self, env: Environment):
        """
        Initialize the output handler.

        Parameters
        ----------
        env : Environment
            Locust Environment instance containing the OpenTelemetry meter
            and instrument registry.
        """
        super().__init__(env)

    def record_event(
        self, tl_type: TelemetryEventsEnum, *args: Any, **kwargs: Any
    ) -> None:
        """
        Record a lifecycle event as a counter data point.

        Parameters
        ----------
        tl_type : TelemetryEventsEnum
            The lifecycle event being recorded (e.g., test.start, test.stop).
        *args : Any
            Additional unused arguments.
        **kwargs : Any
            Attributes to attach to the recorded metric.
        """
        context = self.get_context(active=True)
        instrument = self.env.otel_registry.get(TelemetryEventsEnum.TEST)

        if not instrument:
            logger.error("[otel] Event metric not registered: %s", tl_type.value)
            raise OtelMetricNotRegisteredError(
                f"Metric not registered: {tl_type.value}"
            )

        instrument.add(1, attributes={"event": tl_type.value, **context, **kwargs})
        logger.debug("[otel] Recorded event: %s", tl_type.value)

    def record_metrics(
        self, tl_type: TelemetryMetricsEnum, *args: Any, **kwargs: Any
    ) -> None:
        """
        Record request or custom metrics.

        Parameters
        ----------
        tl_type : TelemetryMetricsEnum
            The metric being recorded (e.g., request_success).
        *args : Any
            Positional arguments containing metric values (e.g., response time).
        **kwargs : Any
            Attributes to attach to the recorded metric.
        """
        context = self.get_context(active=True)
        instrument = self.env.otel_registry.get(tl_type)

        if not instrument:
            logger.error("[otel] Metric not registered: %s", tl_type.value)
            raise OtelMetricNotRegisteredError(
                f"Metric not registered: {tl_type.value}"
            )

        instrument.record(
            args[0],
            attributes={"metric": tl_type.value, **context, **kwargs},
        )


class OtelLifecycleHandler(BaseLifecycleHandler):
    """
    OpenTelemetry lifecycle handler.

    Extends the base lifecycle handler to register OTEL instruments for
    test events and user counts.
    """

    def __init__(self, output: OtelOutputHandler, env: Environment):
        super().__init__(output, env)
        self.output: OtelOutputHandler = output
        self.register_instruments()

    def register_instruments(self) -> None:
        """
        Register lifecycle instruments.

        Notes
        -----
        Instruments begin collecting data immediately upon registration.
        """
        self.env.otel_registry.extend(
            [
                # Test lifecycle events as counters
                (
                    TelemetryEventsEnum.TEST,
                    "1",
                    h.create_otel_counter,
                    None,
                ),
                # Active user count as an observable gauge
                (
                    TelemetryMetricsEnum.USER,
                    "1",
                    h.create_otel_observable_gauge,
                    [self._user_count_callback],
                ),
            ]
        )
        logger.info("[otel] Registered lifecycle metrics successfully.")

    def _user_count_callback(self, options=None) -> List[Observation]:
        """
        Observable callback for current active user count.

        Returns
        -------
        list[Observation]
            Single observation containing the active user count.
        """
        return [Observation(self.env.runner.user_count, self.output.get_context())]


class OtelSystemMetricsHandler(BaseSystemMetricsHandler):
    """
    OpenTelemetry handler for system-level metrics.

    Collects CPU usage, memory usage, and network I/O using psutil and
    reports them via Observable Gauges.
    """

    _process: psutil.Process = psutil.Process()

    def __init__(self, output: OtelOutputHandler, env: Environment):
        """
        Initialize the system metrics handler.

        Parameters
        ----------
        output : OtelOutputHandler
            Reference to the output handler for recording metrics.
        env : Environment
            Locust Environment instance.
        """
        super().__init__(output, env)
        self.output: OtelOutputHandler = output
        self.register_instruments()

    def register_instruments(self) -> None:
        """
        Register system metrics instruments.

        Notes
        -----
        psutil is "warmed up" to avoid the first-call zero-value issue.
        """
        h.warmup_psutil(self._process)
        self.env.otel_registry.extend(
            [
                (
                    TelemetryMetricsEnum.NETWORK,
                    "By",
                    h.create_otel_observable_gauge,
                    [self._network_usage_callback],
                ),
                (
                    TelemetryMetricsEnum.MEMORY,
                    "By",
                    h.create_otel_observable_gauge,
                    [self._memory_usage_callback],
                ),
                (
                    TelemetryMetricsEnum.CPU,
                    "%",
                    h.create_otel_observable_gauge,
                    [self._cpu_usage_callback],
                ),
            ]
        )
        logger.info("[otel] Registered system metrics successfully.")

    def start(self) -> None:
        """
        Start system metrics collection (no-op, provided for interface compliance).
        """

    def stop(self) -> None:
        """
        Stop system metrics collection (no-op, provided for interface compliance).
        """

    def _network_usage_callback(self, options=None) -> List[Observation]:
        """
        Callback for network I/O statistics.

        Returns
        -------
        list[Observation]
            Observations for bytes sent and received.
        """
        io = psutil.net_io_counters()
        ctx = self.output.get_context()
        return [
            Observation(io.bytes_sent, {**ctx, "direction": "sent"}),
            Observation(io.bytes_recv, {**ctx, "direction": "recv"}),
        ]

    def _memory_usage_callback(self, options=None) -> List[Observation]:
        """
        Callback for process memory usage.

        Returns
        -------
        list[Observation]
            Observation for memory usage in MiB.
        """
        memory_mib = h.convert_bytes_to_mib(self._process.memory_info().rss)
        return [Observation(memory_mib, self.output.get_context())]

    def _cpu_usage_callback(self, options=None) -> List[Observation]:
        """
        Callback for process CPU usage.

        Returns
        -------
        list[Observation]
            Observation for CPU utilization percentage.
        """
        return [Observation(self._process.cpu_percent(), self.output.get_context())]


class OtelRequestHandler(BaseRequestHandler):
    """
    OpenTelemetry handler for request-level metrics.

    Registers histograms for request success and failure durations,
    and records metrics for each request event.
    """

    def __init__(self, output: OtelOutputHandler, env: Environment):
        """
        Initialize the request metrics handler.

        Parameters
        ----------
        output : OtelOutputHandler
            Reference to the output handler for recording metrics.
        env : Environment
            Locust Environment instance.
        """
        super().__init__(output, env)
        self.output: OtelOutputHandler = output
        self.register_instruments()

    def register_instruments(self) -> None:
        """
        Register request metrics instruments.

        Notes
        -----
        Instruments begin collecting data immediately upon registration.
        """
        self.env.otel_registry.extend(
            [
                (
                    TelemetryMetricsEnum.REQUEST_SUCCESS,
                    "ms",
                    h.create_otel_histogram,
                    None,
                ),
                (
                    TelemetryMetricsEnum.REQUEST_ERROR,
                    "ms",
                    h.create_otel_histogram,
                    None,
                ),
            ]
        )
        logger.info("[otel] Registered request metrics successfully.")

    def start(self) -> None:
        """
        Start request metrics collection (no-op, provided for interface compliance).
        """

    def stop(self) -> None:
        """
        Stop request metrics collection (no-op, provided for interface compliance).
        """

    def on_request(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle a request event and record request duration.

        Parameters
        ----------
        *args : Any
            Additional unused arguments.
        **kwargs : Any
            Keyword arguments containing request metadata,
            such as response_time, name, and exception.
        """
        response = kwargs.get("response")
        is_error = bool(kwargs.get("exception"))
        metric = (
            TelemetryMetricsEnum.REQUEST_ERROR
            if is_error
            else TelemetryMetricsEnum.REQUEST_SUCCESS
        )

        self.output.record_metrics(
            metric,
            kwargs.get("response_time"),
            endpoint=kwargs.get("name"),
            status_code=response.status_code if response else 500,
        )
