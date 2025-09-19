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
from typing import Any, Callable, Dict, List

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
        self.meter = self.env.otel_meter

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
        """
        instrument = kind(self.meter, metric.value, metric.value, unit)
        self._instrument_registry[metric] = instrument
        logger.info(f"[otel] Registered {kind} '{metric.value}'.")
        return instrument

    def add_callbacks(
        self,
        metric: TelemetryMetricsEnum | TelemetryEventsEnum,
        callbacks: List[Callable],
    ) -> None:
        """
        Add callbacks to a registered metric instrument.

        Parameters
        ----------
        metric : OtelMetricDefinition
            The metric to which callbacks will be attached.
        callbacks : list[Callable]
            Callback functions returning Observations.
        """
        instrument = self._instrument_registry.get(metric)
        if not instrument:
            raise ValueError(f"Metric '{metric.value}' is not registered yet.")
        instrument._callbacks = callbacks

    def remove_callbacks(
        self, metric: TelemetryMetricsEnum | TelemetryEventsEnum
    ) -> None:
        """
        Remove all callbacks from a registered metric instrument.

        Parameters
        ----------
        metric : OtelMetricDefinition
            The metric from which callbacks will be removed.
        """
        instrument = self._instrument_registry.get(metric)
        if not instrument:
            raise ValueError(f"Metric '{metric.value}' is not registered yet.")

        # ⚠️ Using _callbacks (private API) because OpenTelemetry SDK does not
        # support unregistering callbacks officially.
        instrument._callbacks = []


class OtelLifecycleHandler(BaseLifecycleHandler):
    """
    OpenTelemetry lifecycle handler.

    For OTel the default implementation in BaseLifecycleHandler is sufficient.
    """

    def __init__(self, output: OtelOutputHandler, env: Environment):
        super().__init__(output, env)
        self.output: OtelOutputHandler = output
        self._register_event_metrics()

    def _register_event_metrics(self) -> None:
        """
        Register event metrics instrument with the output handler

        Metrics:
        - Test events metric
        - Requests duration metric
        """
        # Test events as counters
        self.output.register_metric(
            metric=TelemetryEventsEnum.TEST,
            unit="1",
            kind=h.create_otel_counter,
        )

        # Register request duration as histogram
        self.output.register_metric(
            metric=TelemetryMetricsEnum.REQUEST,
            unit="ms",
            kind=h.create_otel_histogram,
        )


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

        self._register_system_metrics()

    def _register_system_metrics(self) -> None:
        """
        Register system metric instruments (gauges).

        Metrics:
        - CPU usage
        - Memory usage
        - Network bytes sent/received
        """
        for metric, unit, kind, _ in self._system_metrics_definition:
            self.output.register_metric(
                metric=metric,
                unit=unit,
                kind=kind,
            )
        logger.info("[otel] Registered all the system metrics")

    def start(self) -> None:
        """
        Start collecting system metrics by adding callbacks.
        """
        h.warmup_psutil(self._process)
        for metric, _, _, callbacks in self._system_metrics_definition:
            self.output.add_callbacks(metric=metric, callbacks=callbacks)
        logger.info("[otel] Registered system metrics callbacks")

    def stop(self) -> None:
        """
        Stop collecting system metrics by removing callbacks.
        """
        for metric, _, _, _ in self._system_metrics_definition:
            self.output.remove_callbacks(metric)
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
                TelemetryMetricsEnum.USER,
                "1",
                h.create_otel_observable_gauge,
                [self._user_count_callback],
            ),
        )

        self._register_request_metrics()

    def _register_request_metrics(self) -> None:
        """
        Register request-related metric instruments.

        Metrics:
        - Request count
        - Error count
        - Active user count
        - RPS (gauge)
        - FPS (gauge)
        """
        for metric, unit, kind, _ in self._request_metrics_definition:
            self.output.register_metric(
                metric=metric,
                unit=unit,
                kind=kind,
            )
        logger.info("[otel] Registered all the request metrics")

    def start(self) -> None:
        """
        Start collecting request metrics by adding callbacks.
        """
        for metric, _, _, callbacks in self._request_metrics_definition:
            self.output.add_callbacks(metric=metric, callbacks=callbacks)

        logger.info("[otel] Registered request metrics callbacks")

    def stop(self) -> None:
        """
        Stop collecting request metrics by removing callbacks.
        """
        for metric, _, _, _ in self._request_metrics_definition:
            self.output.remove_callbacks(metric)
        logger.info("[otel] Unregistered request metrics callbacks")

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
        self.output.record_metrics(
            TelemetryMetricsEnum.REQUEST,
            kwargs.get("response_time"),
            exception=bool(kwargs.get("exception")),
            endpoint=kwargs.get("name"),
        )

    def _user_count_callback(self, options=None) -> List[Observation]:
        """
        Observable callback for current active user count.

        Returns
        -------
        list[Observation]
            Observation containing user count.
        """
        return [Observation(self.env.runner.user_count, self.output.get_run_context())]
