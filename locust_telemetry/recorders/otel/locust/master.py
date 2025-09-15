import logging
import time
from typing import Any, ClassVar, Iterable, Optional

import gevent
import psutil
from locust.env import Environment
from opentelemetry.metrics import CallbackOptions, Observation

from locust_telemetry.core.recorder import TelemetryBaseRecorder
from locust_telemetry.recorders.otel.locust.metrics import OtelMetricsDefinition

logger = logging.getLogger(__name__)


class MasterLocustOtelRecorder(TelemetryBaseRecorder):
    """
    OpenTelemetry recorder for Locust MasterRunner.

    Responsibilities
    ----------------
    - Collect test lifecycle events (start, stop, spawning complete).
    - Record request statistics (total, per-endpoint, errors).
    - Track system metrics (CPU, memory, network I/O).
    - Spawn background loop for periodic stats logging.
    - Register observable gauge callbacks for dynamic system metrics.
    - Ensure metrics are enriched with recorder context (run_id, testplan, etc.).

    Usage
    -----
    This recorder is instantiated by the telemetry plugin system and is only
    active when the current Locust runner is a ``MasterRunner``. It integrates
    with Locust event hooks and periodically exports metrics via the configured
    OpenTelemetry SDK.

    Notes
    -----
    - Runs only on master node in distributed Locust setups.
    - Relies on ``psutil`` for system process and network metrics.
    - Periodic stats interval defaults to 5 seconds (configurable).
    """

    name: ClassVar[str] = "master_otel_recorder"

    def __init__(
        self,
        env: Environment,
        metrics: Optional[OtelMetricsDefinition] = None,
        stats_interval: int = 5,
    ) -> None:
        """
        Initialize the OpenTelemetry recorder for Locust master node.

        Parameters
        ----------
        env : Environment
            The Locust environment instance.
        metrics : OtelMetricsDefinition, optional
            Metric instruments. If not provided, a default set will be created.
        stats_interval : int, default=5
            Interval in seconds for periodic request stats logging.
        """
        super().__init__(env)

        self.metrics: OtelMetricsDefinition = metrics or OtelMetricsDefinition()
        self._stats_interval: int = stats_interval

        self._request_stats_logger: Optional[gevent.Greenlet] = None
        self.process = psutil.Process()

        # Register gauge callbacks
        self._register_observable_callbacks()

        # Master-only event listeners
        env.events.test_start.add_listener(self.on_test_start)
        env.events.test_stop.add_listener(self.on_test_stop)
        env.events.spawning_complete.add_listener(self.on_spawning_complete)

    # -----------------------------
    # Utilities
    # -----------------------------

    @property
    def now_ms(self) -> int:
        """
        Current wall-clock time in milliseconds.

        Returns
        -------
        int
            Unix timestamp in milliseconds.
        """
        return int(time.time() * 1000)

    def _register_observable_callbacks(self) -> None:
        """
        Register callbacks for all observable gauges.

        Notes
        -----
        Each gauge is bound to a callback that yields ``Observation`` objects
        with system metrics or runtime values.
        """
        self.metrics.requests.user_count_gauge.add_callback(self._get_user_count)
        self.metrics.system.cpu_usage_gauge.add_callback(self._get_cpu_usage)
        self.metrics.system.memory_usage_gauge.add_callback(self._get_memory_usage)
        self.metrics.system.network_bytes_sent.add_callback(self._get_network_usage)
        self.metrics.system.network_bytes_received.add_callback(self._get_network_usage)

    def _get_user_count(self, _: CallbackOptions) -> Iterable[Observation]:
        """
        Callback for user count gauge.

        Parameters
        ----------
        _ : CallbackOptions
            OpenTelemetry callback options (unused).

        Yields
        ------
        Observation
            Number of active Locust users with recorder context.
        """
        if self.env.runner:
            yield Observation(self.env.runner.user_count, self.recorder_context())

    def _get_cpu_usage(self, _: CallbackOptions) -> Iterable[Observation]:
        """
        Callback for CPU usage gauge.

        Parameters
        ----------
        _ : CallbackOptions
            OpenTelemetry callback options (unused).

        Yields
        ------
        Observation
            CPU usage percentage of the Locust process.
        """
        yield Observation(self.process.cpu_percent(), self.recorder_context())

    def _get_memory_usage(self, _: CallbackOptions) -> Iterable[Observation]:
        """
        Callback for memory usage gauge.

        Parameters
        ----------
        _ : CallbackOptions
            OpenTelemetry callback options (unused).

        Yields
        ------
        Observation
            Resident memory usage (RSS) of the Locust process in bytes.
        """
        yield Observation(self.process.memory_info().rss, self.recorder_context())

    def _get_network_usage(self, _: CallbackOptions) -> Iterable[Observation]:
        """
        Callback for network I/O gauges.

        Parameters
        ----------
        _ : CallbackOptions
            OpenTelemetry callback options (unused).

        Yields
        ------
        Observation
            Bytes sent and received by the Locust process.
        """
        io_counters = psutil.net_io_counters()
        attrs = self.recorder_context()
        yield Observation(io_counters.bytes_sent, {**attrs, "direction": "sent"})
        yield Observation(io_counters.bytes_recv, {**attrs, "direction": "received"})

    # -----------------------------
    # Event handlers
    # -----------------------------

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle the ``test_start`` event and start background stats collection.

        Notes
        -----
        - Records initial test start metrics.
        - Spawns greenlet for periodic request stats logging.
        """
        attrs = {**self.recorder_context(), "event_type": "test_start"}
        self.metrics.events.test_start_event.record(self.now_ms, attributes=attrs)
        self.metrics.events.test_event.record(self.now_ms, attributes=attrs)

        self._request_stats_logger = gevent.spawn(self._log_request_stats)
        logger.info("Test started - metrics recording initiated", extra=attrs)

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle the ``test_stop`` event and stop background stats collection.

        Notes
        -----
        - Stops the background greenlet.
        - Flushes final request and error statistics.
        """
        self._stop_request_stats_logger()

        self._log_total_stats(final=True)
        self._log_entry_stats()
        self._log_error_stats()

        logger.info(
            "Test stopped - final metrics recorded", extra=self.recorder_context()
        )

    def on_spawning_complete(self, user_count: int) -> None:
        """
        Handle the ``spawning_complete`` event.

        Parameters
        ----------
        user_count : int
            Final number of spawned users.

        Notes
        -----
        Records spawning complete and test event metrics.
        """
        attrs = {**self.recorder_context(), "user_count": str(user_count)}
        self.metrics.events.spawn_complete_event.record(self.now_ms, attributes=attrs)
        self.metrics.events.test_event.record(self.now_ms, attributes=attrs)

        logger.info("Spawning complete", extra=attrs)

    # -----------------------------
    # Stats logging
    # -----------------------------

    def _stop_request_stats_logger(self) -> None:
        """
        Stop the background request stats logger if running.

        Notes
        -----
        The greenlet is killed cleanly if active.
        """
        if self._request_stats_logger:
            self._request_stats_logger.kill()
            self._request_stats_logger = None

    def _log_total_stats(self, final: bool = False) -> None:
        """
        Record aggregated request statistics as metrics.

        Parameters
        ----------
        final : bool, default=False
            If True, log indicates final flush at test stop.
        """
        if not self.env.stats or not self.env.runner:
            return

        stats = self.env.stats.total
        attrs = self.recorder_context()

        self.metrics.requests.requests_counter.add(stats.num_requests, attributes=attrs)
        self.metrics.requests.errors_counter.add(stats.num_failures, attributes=attrs)

        if stats.num_requests > 0:
            self.metrics.requests.request_duration.record(
                stats.avg_response_time, attributes=attrs
            )

        if final:
            logger.debug("Final total stats recorded", extra=attrs)

    def _log_entry_stats(self) -> None:
        """
        Record per-endpoint request statistics.

        Notes
        -----
        Includes metrics grouped by endpoint name and HTTP method.
        """
        for (name, method), stats in self.env.stats.entries.items():
            attrs = {
                **self.recorder_context(),
                "endpoint": name,
                "http_method": method,
            }
            self.metrics.requests.requests_counter.add(
                stats.num_requests, attributes=attrs
            )

    def _log_error_stats(self) -> None:
        """
        Record error statistics.

        Notes
        -----
        Metrics include error type, endpoint, and HTTP method.
        """
        for _, error in self.env.stats.errors.items():
            attrs = {
                **self.recorder_context(),
                "error_type": error.error,
                "endpoint": error.name,
                "http_method": error.method,
            }
            self.metrics.requests.errors_counter.add(
                error.occurrences, attributes=attrs
            )

    def _log_request_stats(self) -> None:
        """
        Background loop that records request stats at configured intervals.

        Notes
        -----
        - Runs until stopped via greenlet kill.
        - Interval is controlled by ``stats_interval`` argument.
        """
        try:
            while True:
                if not self.env.runner:
                    return
                self._log_total_stats(final=False)
                gevent.sleep(self._stats_interval)
        except gevent.GreenletExit:
            logger.info("Request stats logger stopped cleanly")
