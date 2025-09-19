"""
OpenTelemetry handlers for Locust.

This module provides handler implementations for lifecycle events, system
metrics, request metrics, and output in the context of OpenTelemetry.
These handlers are used by the OTEL recorders for both master and worker
nodes to collect and export telemetry data to an OTLP endpoint.

Classes
-------
OtelLifecycleHandler
    Registers and records lifecycle event metrics (e.g., test events,
    request durations).
OtelOutputHandler
    Central registry for metrics; manages creation, recording, and
    cleanup of instruments.
OtelRequestHandler
    Registers request-related metrics (count, errors, RPS/FPS) and records request
     durations.
OtelSystemMetricsHandler
    Registers and reports system-level metrics (CPU, memory, network I/O) via callbacks.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

import psutil
from locust.env import Environment
from locust.runners import WorkerRunner
from opentelemetry.metrics import Observation

from locust_telemetry.common import helpers as h
from locust_telemetry.core.events import TelemetryEventsEnum, TelemetryMetricsEnum
from locust_telemetry.core.handlers import (
    BaseLifecycleHandler,
    BaseOutputHandler,
    BaseRequestHandler,
    BaseSystemMetricsHandler,
)

logger = logging.getLogger(__name__)


class OtelOutputHandler(BaseOutputHandler):
    """
    OpenTelemetry output handler for recording lifecycle events
    and metrics.

    Manages registration and cleanup of gauges, counters, and up-down counters.
    """

    def __init__(self, env: Environment):
        """
        Initialize the output handler.

        Parameters
        ----------
        env : Environment
            Locust Environment instance containing the OpenTelemetry meter.
        """
        super().__init__(env)

        # Registered metric instruments
        self._instrument_registry: Dict[
            TelemetryEventsEnum | TelemetryMetricsEnum, h.InstrumentType
        ] = {}

    def record_event(
        self, tl_type: TelemetryEventsEnum, *args: Any, **kwargs: Any
    ) -> None:
        """
        Record a lifecycle event as a counter data point.

        Parameters
        ----------
        tl_type : TelemetryEvent
            The lifecycle event being recorded.
        *args : Any
            Additional unused arguments.
        **kwargs : Any
            Attributes to attach to the recorded metric.
        """
        context = self.get_run_context()
        instrument = self._instrument_registry.get(TelemetryEventsEnum.TEST)
        instrument.add(1, attributes={"event": tl_type.value, **context, **kwargs})
        logger.debug(f"[otel] Recorded event: {tl_type.value}")

    def record_metrics(
        self, tl_type: TelemetryMetricsEnum, *args: Any, **kwargs: Any
    ) -> None:
        """
        Record request metrics such as duration.

        Parameters
        ----------
        tl_type : TelemetryMetric
            The metric being recorded.
        *args : Any
            Additional metric values (e.g., response time).
        **kwargs : Any
            Attributes to attach to the recorded metric.
        """
        context = self.get_run_context()
        instrument = self._instrument_registry.get(tl_type)
        instrument.record(
            args[0],
            attributes={"metrics": tl_type.value, **context, **kwargs},
        )

    def register_metric(
        self,
        metric: TelemetryMetricsEnum | TelemetryEventsEnum,
        unit: str,
        kind: Callable,
        callbacks: Optional[List[Callable]] = None,
    ) -> Any:
        """
        Register an OpenTelemetry metric instrument.

        Parameters
        ----------
        metric : OtelMetricDefinition
            Metric definition (name + description).
        unit : str
            Unit of measurement (e.g., "By", "%", "requests").
        kind : Callable
            Metric constructor function (e.g., `h.create_otel_counter`,
            `h.create_otel_histogram`)
        callbacks : Callbacks
            Register callbacks if any
        """
        meter = self.env.otel_meter
        instrument = kind(
            meter=meter,
            name=metric.value,
            description=metric.value,
            unit=unit,
            callbacks=callbacks,
        )
        self._instrument_registry[metric] = instrument
        logger.info(f"[otel] Registered {metric.value}:{kind.__name__} ")
        return instrument

    def deregister_metric(
        self, metric: TelemetryMetricsEnum | TelemetryEventsEnum
    ) -> h.InstrumentType | None:
        """
        Deregister an OpenTelemetry metric instrument.

        Parameters
        ----------
        metric : OtelMetricDefinition
            Metric definition (name + description).
        """
        instrument = self._instrument_registry.pop(metric, None)
        if instrument and hasattr(instrument, "_callbacks"):
            instrument._callbacks = []
        logger.info(f"[otel] Deregistered {metric.value}")
        return instrument


class OtelLifecycleHandler(BaseLifecycleHandler):
    """
    OpenTelemetry lifecycle handler.

    For OTel the default implementation in BaseLifecycleHandler is sufficient.
    """

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

        self._lifecycle_metrics = (
            # Test events as counters
            (TelemetryEventsEnum.TEST, "1", h.create_otel_counter, None),
            # User spawning events
            (
                TelemetryMetricsEnum.USER,
                "1",
                h.create_otel_observable_gauge,
                [self._user_count_callback],
            ),
        )

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        On Test start register all the metrics
        """
        for metric, unit, kind, callbacks in self._lifecycle_metrics:
            self.output.register_metric(metric, unit, kind, callbacks)
        super().on_test_start(*args, **kwargs)

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        On Test stop deregister all the metrics
        """
        super().on_test_stop(*args, **kwargs)
        for metric, _, _, _ in self._lifecycle_metrics:
            self.output.deregister_metric(metric)

    def _user_count_callback(self, options=None) -> List[Observation]:
        """
        Observable callback for current active user count.

        Returns
        -------
        list[Observation]
            Observation containing user count.
        """
        return [Observation(self.env.runner.user_count, self.output.get_run_context())]


class OtelSystemMetricsHandler(BaseSystemMetricsHandler):
    """
    OpenTelemetry handler for system-level metrics.

    Collects CPU usage, memory usage, and network I/O using psutil
    and reports them via Observable Gauges.
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

        self._system_metrics_definition = (
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
        )

    def start(self) -> None:
        """
        Start collecting system metrics by adding callbacks.
        """
        for metric, unit, kind, callbacks in self._system_metrics_definition:
            self.output.register_metric(metric, unit, kind, callbacks)
        h.warmup_psutil(self._process)
        logger.info("[otel] Registered all the system metrics")

    def stop(self) -> None:
        """
        Stop collecting system metrics by removing callbacks.
        """
        for metric, _, _, _ in self._system_metrics_definition:
            self.output.deregister_metric(metric)
        logger.info("[otel] Unregistered system metrics callbacks")

    def _network_usage_callback(self, options=None) -> List[Observation]:
        """
        Callback for network I/O statistics.

        Returns
        -------
        list[Observation]
            Observations for bytes sent and received.
        """
        io = psutil.net_io_counters()
        ctx = self.output.get_run_context()
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
        return [Observation(memory_mib, self.output.get_run_context())]

    def _cpu_usage_callback(self, options=None) -> List[Observation]:
        """
        Callback for process CPU usage.

        Returns
        -------
        list[Observation]
            Observation for CPU utilization percentage.
        """
        return [Observation(self._process.cpu_percent(), self.output.get_run_context())]


class OtelRequestHandler(BaseRequestHandler):
    """
    OpenTelemetry handler for request-level metrics.

    Delegates recording of request duration to the output handler.
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

        # Request metrics definition, handled by this handler
        self._request_metrics_definition = (
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
        )

    def start(self) -> None:
        """
        Start collecting request metrics by adding callbacks.
        """
        if not isinstance(self.env.runner, WorkerRunner):
            return
        for metric, unit, kind, callbacks in self._request_metrics_definition:
            self.output.register_metric(metric, unit, kind, callbacks)
        logger.info("[otel] Registered all the request metrics")

    def stop(self) -> None:
        """
        Stop collecting request metrics by removing callbacks.
        """
        if not isinstance(self.env.runner, WorkerRunner):
            return
        for metric, _, _, _ in self._request_metrics_definition:
            self.output.deregister_metric(metric)
        logger.info("[otel] Unregistered request metrics")

    def on_request(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle a request event and record request duration.

        Parameters
        ----------
        *args : Any
            Additional unused arguments.
        **kwargs : Any
            Keyword arguments containing request metadata,
            such as response_time and exception flag.
        """
        # This should not throw any error because locust should always send response
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
