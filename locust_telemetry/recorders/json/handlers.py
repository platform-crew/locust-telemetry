"""
JSON telemetry handlers for Locust.
This module provides handler implementations for lifecycle events, system
metrics, request metrics, and structured JSON output. These handlers are
used by the JSON telemetry recorders for both master and worker nodes.
"""

import logging
from typing import Any, Optional

import gevent
import psutil
from locust.runners import WorkerRunner

from locust_telemetry.common import helpers as h
from locust_telemetry.core.events import TelemetryEventsEnum, TelemetryMetricsEnum
from locust_telemetry.core.handlers import (
    BaseLifecycleHandler,
    BaseOutputHandler,
    BaseRequestHandler,
    BaseSystemMetricsHandler,
)
from locust_telemetry.recorders.json.constants import (
    REQUEST_STATS_TYPE_CURRENT,
    REQUEST_STATS_TYPE_ENDPOINT,
    REQUEST_STATS_TYPE_FINAL,
    REQUEST_STATUS_ERROR,
    REQUEST_STATUS_SUCCESS,
    TEST_STOP_BUFFER_FOR_GRAPHS,
)

logger = logging.getLogger(__name__)


class JsonTelemetryOutputHandler(BaseOutputHandler):
    """
    Output handler for JSON-based telemetry logging.

    Responsibilities
    ----------------
    - Log lifecycle events and system/request metrics in JSON format.
    - Enrich logs with run-level context including run ID, testplan,
      and source (master/worker).
    """

    def log_telemetry(self, event_type: str, event_name: str, **kwargs: Any) -> None:
        """
        Log a telemetry data as json

        Parameters
        ----------
        event_type : str
            The telemetry event type either 'event' or 'metrics'.
        event_name : str
            Name of the telemetry event or metrics
        **kwargs : dict
            Additional event/metrics metadata.
        """
        payload = {**self.get_context(active=True), **kwargs}
        logger.info(
            f"Recording telemetry {event_type}: {event_name}",
            extra={
                "telemetry": {
                    "telemetry_type": event_type,
                    "telemetry_name": event_name,
                    **payload,
                }
            },
        )

    def record_event(
        self, tl_type: TelemetryEventsEnum, *args: Any, **kwargs: Any
    ) -> None:
        """
        Record a telemetry event in JSON format.

        Parameters
        ----------
        tl_type : TelemetryEvent
            The telemetry event enum.
        *args : tuple
            Additional positional arguments for the event.
        **kwargs : dict
            Additional event metadata.
        """
        self.log_telemetry("event", tl_type.value, **kwargs)

    def record_metrics(
        self, tl_type: TelemetryMetricsEnum, *args: Any, **kwargs: Any
    ) -> None:
        """
        Record a telemetry metric in JSON format.

        Parameters
        ----------
        tl_type : TelemetryMetric
            The telemetry metric enum.
        *args : tuple
            Additional positional arguments for the metric.
        **kwargs : dict
            Metric-specific attributes such as `value` and `unit`.
        """
        self.log_telemetry("metrics", tl_type.value, **kwargs)


class JsonTelemetryLifecycleHandler(BaseLifecycleHandler):
    """
    Lifecycle handler for JSON telemetry.

    This class inherits from `LifecycleHandlerBase` and handles
    Locust test lifecycle events. For JSON telemetry, lifecycle events
    are forwarded to the output handler for structured logging.

    Custom behavior:
    On test stop, adjusts the stop timestamp to account for a
    buffer used in JSON graphs, and emits a `SPAWNING_COMPLETE` event.

    Attributes
    ----------
    output : OutputHandlerBase
        Output handler responsible for recording telemetry events.
    env : Environment
        The Locust environment instance.
    """

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle the `test_stop` event for JSON telemetry.

        Adjusts the test stop time by `TEST_STOP_BUFFER_FOR_GRAPHS` seconds
        to allow for post-test graph updates, then forwards the event
        to the output handler.

        Parameters
        ----------
        *args : Any
            Positional arguments passed by Locust.
        **kwargs : Any
            Additional keyword arguments passed by Locust.
        """
        end_time = h.get_utc_time_with_buffer(
            seconds_buffer=TEST_STOP_BUFFER_FOR_GRAPHS
        )

        self.output.record_event(
            TelemetryEventsEnum.TEST_STOP, *args, end_time=end_time, **kwargs
        )
        logger.info("[json] Recorded test stop event with adjusted end time.")


class JsonTelemetrySystemMetricsHandler(BaseSystemMetricsHandler):
    """
    System metrics handler for JSON telemetry.

    Responsibilities
    ----------------
    - Periodically capture process-level metrics (CPU and memory usage).
    - Forward metrics to the JSON output handler.
    - Run metrics collection in a background greenlet for non-blocking execution.
    """

    _system_metrics_gevent: Optional[gevent.Greenlet] = None
    _process: psutil.Process = psutil.Process()

    def start(self) -> None:
        """
        Start system metrics collection.

        Spawns a greenlet that periodically collects CPU and memory metrics.
        """
        # Warmup psutil to avoid starting from zero
        h.warmup_psutil(self._process)
        self._system_metrics_gevent = gevent.spawn(self._gevent_loop)

    def stop(self) -> None:
        """
        Stop system metrics collection.

        Terminates the greenlet collecting system metrics.
        Logs a warning if the collection loop was never started.
        """
        if self._system_metrics_gevent is None:
            logger.warning("[json] Gevent loop never started")
            return
        self._system_metrics_gevent.kill()
        self._system_metrics_gevent = None

    def _gevent_loop(self) -> None:
        """
        Background loop for capturing system metrics.

        This method runs inside a greenlet and periodically records:
        - CPU usage (percent)
        - Memory usage (MiB)

        The interval between recordings is defined by
        ``self.env.parsed_options.lt_stats_recorder_interval``.

        Handles graceful termination on `GreenletExit` and logs any exceptions.
        """
        try:
            while True:
                io = psutil.net_io_counters()
                cpu_usage = self._process.cpu_percent()
                # Convert bytes to MiB
                memory_usage = h.convert_bytes_to_mib(self._process.memory_info().rss)
                self.output.record_metrics(
                    TelemetryMetricsEnum.CPU, value=cpu_usage, unit="percent"
                )
                self.output.record_metrics(
                    TelemetryMetricsEnum.MEMORY, value=memory_usage, unit="MiB"
                )
                self.output.record_metrics(
                    TelemetryMetricsEnum.NETWORK,
                    value=io.bytes_sent,
                    unit="MiB",
                    direction="sent",
                )
                self.output.record_metrics(
                    TelemetryMetricsEnum.NETWORK,
                    value=io.bytes_recv,
                    unit="MiB",
                    direction="recv",
                )
                gevent.sleep(self.env.parsed_options.lt_stats_recorder_interval)
        except gevent.GreenletExit:
            logger.info("[json] System metrics collection terminated gracefully")
        except Exception:
            logger.exception("[json] System metrics collection loop failed")
            raise


class JsonTelemetryRequestHandler(BaseRequestHandler):
    """
    JSON telemetry handler for Locust request events/metrics.

    This handler periodically collects aggregate request metrics and forwards
    them to the output handler in a format suitable for JSON logging. It also
    implements the `RequestHandlerBase` interface for individual request events,
    though in JSON telemetry no action is needed per-request.

    Attributes
    ----------
    _request_metrics_gevent : Optional[gevent.Greenlet]
        Background greenlet for periodically collecting request metrics.
    """

    _request_metrics_gevent: Optional[gevent.Greenlet] = None

    def start(self) -> None:
        """
        Start periodic request metrics collection.

        Spawns a background greenlet that logs aggregate request statistics
        at the configured interval.
        """
        # Since this collects stats from master, there is no need to run in worker node
        if isinstance(self.env.runner, WorkerRunner):
            return

        self._request_metrics_gevent = gevent.spawn(self._gevent_loop)

    def stop(self) -> None:
        """
        Stop request metrics collection.

        Terminates the greenlet collecting request metrics. Logs a warning
        if the collection loop was never started.
        """
        # Since this collects stats from master, there is no need to run in worker node
        if isinstance(self.env.runner, WorkerRunner):
            return

        if self._request_metrics_gevent is None:
            logger.warning("[json] Gevent loop never started")
            return
        self._request_metrics_gevent.kill()
        self._request_metrics_gevent = None

        # Collect final stats
        self._flush_stats()

    def _flush_stats(self):
        """
        Collect and log the final request statistics at the end of a test.

        Iterates over both successful and error request statistics and records
        them via the output handler. Percentile fields are normalized using
        `add_percentiles`.

        This method is called when stopping the request metrics collection
        greenlet to ensure all final metrics are emitted.
        """
        # Final requests stats
        self.output.record_metrics(
            TelemetryMetricsEnum.REQUEST_STATS,
            stats_type=REQUEST_STATS_TYPE_FINAL,
            user_count=self.env.runner.user_count,
            **h.add_percentiles(self.env.stats.total.to_dict()),
        )

        # Final request success and error stats by endpoint.
        final_stats_types = {
            REQUEST_STATUS_ERROR: self.env.stats.errors,
            REQUEST_STATUS_SUCCESS: self.env.stats.entries,
        }
        for status, stats in final_stats_types.items():
            for _, stat in stats.items():
                self.output.record_metrics(
                    TelemetryMetricsEnum.REQUEST_STATS,
                    stats_type=REQUEST_STATS_TYPE_ENDPOINT,
                    status=status,
                    **h.add_percentiles(stat.to_dict()),
                )

    def _gevent_loop(self) -> None:
        """
        Background loop for periodic request metrics collection.

        Continuously collects total request statistics and sends them
        to the output handler until the greenlet is killed.
        """
        try:
            while True:
                stats = h.add_percentiles(self.env.stats.total.to_dict())
                self.output.record_metrics(
                    TelemetryMetricsEnum.REQUEST_STATS,
                    stats_type=REQUEST_STATS_TYPE_CURRENT,
                    user_count=self.env.runner.user_count,
                    **stats,
                )
                gevent.sleep(self.env.parsed_options.lt_stats_recorder_interval)
        except gevent.GreenletExit:
            logger.info("[json] Request stats logger terminated gracefully")
        except Exception:
            logger.exception("[json] Request metrics collection loop failed")
            raise

    def on_request(self, *args: Any, **kwargs: Any) -> None:
        """
        Handler for individual Locust request events.

        For JSON telemetry, per-request handling is not needed, so this is
        intentionally left empty.

        Parameters
        ----------
        *args : Any
            Positional arguments from Locust request events.
        **kwargs : Any
            Keyword arguments from Locust request events.
        """
