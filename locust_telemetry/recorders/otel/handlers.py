"""
OpenTelemetry handlers for Locust.

This module provides handler implementations for lifecycle events, system
metrics, request metrics, and output in the context of OpenTelemetry.
These handlers are used by the OTEL recorders for both master and worker
nodes to collect and export telemetry data to an OTLP endpoint.

Classes
-------
OtelLifecycleHandler
    Handles Locust test lifecycle events for OTEL.
OtelOutputHandler
    Handles structured telemetry output and export for OTEL.
OtelRequestHandler
    Collects and exports request metrics for OTEL.
OtelSystemMetricsHandler
    Collects and exports system-level metrics (CPU, memory) for OTEL.
"""

import logging
from typing import Any, Callable, Dict, List

import psutil
from locust.env import Environment
from opentelemetry.metrics import Observation

from locust_telemetry.common import helpers as h
from locust_telemetry.core.events import TelemetryEvent, TelemetryMetric
from locust_telemetry.core.handlers import (
    BaseLifecycleHandler,
    BaseOutputHandler,
    BaseRequestHandler,
    BaseSystemMetricsHandler,
)
from locust_telemetry.recorders.otel.constants import OtelMetricDefinition

logger = logging.getLogger(__name__)


class OtelLifecycleHandler(BaseLifecycleHandler):
    """
    OpenTelemetry lifecycle handler.

    For OTel the default implementation in BaseLifecycleHandler is sufficient.
    """

    pass


class OtelOutputHandler(BaseOutputHandler):
    """
    OpenTelemetry output handler for recording lifecycle events
    and metrics.

    Manages registration and cleanup of gauges, and uses histograms
    to capture event timestamps and request durations.
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

        # All the registered gauges
        self._registered_gauges: Dict[str, List] = {}

        # Histograms for lifecycle events
        self.test_event = h.create_otel_histogram(
            self.meter,
            OtelMetricDefinition.TEST_EVENTS.metric_name,
            OtelMetricDefinition.TEST_EVENTS.metric_description,
        )

        # Request duration metrics
        self.request_duration = h.create_otel_histogram(
            self.meter,
            OtelMetricDefinition.REQUEST_DURATION.metric_name,
            OtelMetricDefinition.REQUEST_DURATION.metric_description,
        )

    def record_event(self, tl_type: TelemetryEvent, *args: Any, **kwargs: Any) -> None:
        """
        Record a lifecycle event as a histogram data point.

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
        self.test_event.record(
            h.now_ms(), attributes={"event": tl_type.value, **context, **kwargs}
        )
        logger.debug(f"[otel] Recorded event: {tl_type.value}")

    def record_metrics(
        self, tl_type: TelemetryMetric, *args: Any, **kwargs: Any
    ) -> None:
        """
        Record metrics emitted by handlers. For OTel,
        most metrics are captured by Observable Gauges,
        while request duration is recorded explicitly.

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

        self.request_duration.record(
            args[0] if args else 0,
            attributes={"metrics": tl_type.value, **context, **kwargs},
        )

    def register_gauge(
        self,
        namespace: str,
        metric: OtelMetricDefinition,
        unit: str,
        callbacks: List[Callable],
    ) -> None:
        """
        Register an OpenTelemetry Observable Gauge.

        Parameters
        ----------
        namespace : str
            Logical namespace under which the gauge is registered.
        metric : OtelMetricDefinition
            Metric definition containing name and description.
        unit : str
            Measurement unit (e.g., "By", "%").
        callbacks : List[Callable]
            Callback(s) that return one or more Observations.
        """
        registered_gauges = self._registered_gauges.setdefault(namespace, [])
        registered_gauges.append(
            h.create_otel_observable_gauge(
                self.meter,
                metric.metric_name,
                metric.metric_description,
                unit,
                callbacks=callbacks,
            )
        )
        logger.info(
            f"[otel] Registered gauge {metric.metric_name} in namespace '{namespace}'"
        )

    def clear_registered_gauges(self, namespace: str) -> None:
        """
        Clear all registered Observable Gauges for a given namespace.

        Ensures callbacks are removed to prevent
        memory leaks and stale data collection.

        Parameters
        ----------
        namespace : str
            Logical namespace whose gauges should be cleared.
        """
        registered_gauges = self._registered_gauges.get(namespace, [])
        if not registered_gauges:
            logger.warning(
                f"[otel] No gauges found in namespace '{namespace}' to clear"
            )
            return

        for g in registered_gauges:
            g.callbacks.clear()

        self._registered_gauges[namespace] = []
        logger.info(f"[otel] Cleared gauges in namespace '{namespace}'")


class OtelSystemMetricsHandler(BaseSystemMetricsHandler):
    """
    OpenTelemetry handler for system-level metrics.

    Collects CPU usage, memory usage, and network I/O using
    psutil and reports them via OpenTelemetry Observable Gauges.
    """

    _process: psutil.Process = psutil.Process()
    _gauge_namespace = "system"

    def __init__(self, output: OtelOutputHandler, env: Environment):
        """
        Initialize the system metrics handler.

        Parameters
        ----------
        output : OtelOutputHandler
            Reference to the output handler for recording attributes.
        env : Environment
            Locust Environment instance containing the OpenTelemetry meter.
        """
        super().__init__(output, env)
        self.output: OtelOutputHandler = output  # type narrowing

    def start(self) -> None:
        """
        Start collecting system metrics.

        Registers Observable Gauges for CPU, memory, and network usage.
        """
        h.warmup_psutil(self._process)

        self.output.register_gauge(
            namespace=self._gauge_namespace,
            metric=OtelMetricDefinition.NETWORK_BYTES,
            unit="By",
            callbacks=[self._network_usage_callback],
        )
        self.output.register_gauge(
            namespace=self._gauge_namespace,
            metric=OtelMetricDefinition.MEMORY_USAGE,
            unit="By",
            callbacks=[self._memory_usage_callback],
        )
        self.output.register_gauge(
            namespace=self._gauge_namespace,
            metric=OtelMetricDefinition.CPU_USAGE,
            unit="%",
            callbacks=[self._cpu_usage_callback],
        )
        logger.info("[otel] Registered system metrics gauges")

    def stop(self) -> None:
        """
        Stop collecting system metrics.

        Delegates cleanup of gauges to the output handler.
        """
        self.output.clear_registered_gauges(self._gauge_namespace)
        logger.info("[otel] Unregistered system metrics gauges")

    def _network_usage_callback(self, options=None):
        """
        Callback for reporting network I/O statistics.

        Returns
        -------
        list[Observation]
            Two OpenTelemetry Observations: bytes sent and bytes received,
            each annotated with direction attributes.
        """
        logger.debug("[otel] Collecting network usage")
        current_io = psutil.net_io_counters()
        context = self.output.get_run_context()
        return [
            Observation(current_io.bytes_sent, {**context, "direction": "sent"}),
            Observation(current_io.bytes_recv, {**context, "direction": "rec"}),
        ]

    def _memory_usage_callback(self, options=None):
        """
        Callback for reporting process memory usage.

        Returns
        -------
        list[Observation]
            One OpenTelemetry Observation with current memory usage in MiB.
        """
        logger.debug("[otel] Collecting memory usage")
        memory_mib = h.convert_bytes_to_mib(self._process.memory_info().rss)
        return [Observation(memory_mib, self.output.get_run_context())]

    def _cpu_usage_callback(self, options=None):
        """
        Callback for reporting CPU usage.

        Returns
        -------
        list[Observation]
            One OpenTelemetry Observation with current CPU utilization percentage.
        """
        logger.debug("[otel] Collecting CPU usage")
        return [Observation(self._process.cpu_percent(), self.output.get_run_context())]


class OtelRequestHandler(BaseRequestHandler):
    """
    OpenTelemetry handler for request-level metrics.

    Delegates recording of request duration to the output handler.
    """

    _gauge_namespace: str = "request"

    def __init__(self, output: OtelOutputHandler, env: Environment):
        """
        Initialize the system metrics handler.

        Parameters
        ----------
        output : OtelOutputHandler
            Reference to the output handler for recording attributes.
        env : Environment
            Locust Environment instance containing the OpenTelemetry meter.
        """
        super().__init__(output, env)
        self.output: OtelOutputHandler = output

    def start(self) -> None:
        """
        Start collecting requests metrics.

        Registers Observable Gauges for all the requests related metrics.
        """
        self.output.register_gauge(
            namespace=self._gauge_namespace,
            metric=OtelMetricDefinition.REQUEST_COUNT,
            unit="1",
            callbacks=[self._request_count_callback],
        )
        self.output.register_gauge(
            namespace=self._gauge_namespace,
            metric=OtelMetricDefinition.ERROR_COUNT,
            unit="1",
            callbacks=[self._error_count_callback],
        )
        self.output.register_gauge(
            namespace=self._gauge_namespace,
            metric=OtelMetricDefinition.USER_COUNT,
            unit="1",
            callbacks=[self._user_count_callback],
        )
        self.output.register_gauge(
            namespace=self._gauge_namespace,
            metric=OtelMetricDefinition.RPS,
            unit="1/s",
            callbacks=[self._rps_callback],
        )
        self.output.register_gauge(
            namespace=self._gauge_namespace,
            metric=OtelMetricDefinition.FPS,
            unit="1/s",
            callbacks=[self._fps_callback],
        )
        logger.info("[otel] Registered request metrics gauges")

    def stop(self) -> None:
        """
        Stop collecting requests metrics.

        Delegates cleanup of gauges to the output handler.
        """
        self.output.clear_registered_gauges(self._gauge_namespace)
        logger.info("[otel] Unregistered request metrics gauges")

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
            TelemetryMetric.REQUEST_DURATION,
            kwargs.get("response_time"),
            exception=bool(kwargs.get("exception")),
        )

    def _request_count_callback(self, options=None):
        """
        Observable callback for total number of requests executed.

        Returns
        -------
        list[Observation]
            OpenTelemetry Observation containing the cumulative request count.
        """
        logger.debug("[otel] Collecting request count")
        stats = self.env.stats.total
        return [Observation(stats.num_requests, self.output.get_run_context())]

    def _error_count_callback(self, options=None):
        """
        Observable callback for total number of failed requests.

        Returns
        -------
        list[Observation]
            OpenTelemetry Observation containing the cumulative failure count.
        """
        logger.debug("[otel] Collecting request failure count")
        stats = self.env.stats.total
        return [Observation(stats.num_failures, self.output.get_run_context())]

    def _user_count_callback(self, options=None):
        """
        Observable callback for current active user count.

        Returns
        -------
        list[Observation]
            OpenTelemetry Observation containing user count and associated attributes.
        """
        logger.debug("[otel] Collecting user count")
        stats = self.env.stats.total
        return [Observation(stats.user_count, self.output.get_run_context())]

    def _rps_callback(self, options=None):
        """
        Observable callback for requests per second (RPS).

        Returns
        -------
        list[Observation]
            OpenTelemetry Observation containing the current RPS.
        """
        logger.debug("[otel] Collecting RPS")
        stats = self.env.stats.total
        return [Observation(stats.num_reqs_per_sec, self.output.get_run_context())]

    def _fps_callback(self, options=None):
        """
        Observable callback for failures per second (FPS).

        Returns
        -------
        list[Observation]
            OpenTelemetry Observation containing the current FPS.
        """
        logger.debug("[otel] Collecting FPS")
        stats = self.env.stats.total
        return [Observation(stats.num_fail_per_sec, self.output.get_run_context())]
