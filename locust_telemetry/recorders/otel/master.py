"""
OpenTelemetry metrics recorder for Locust MasterRunner.

This module provides comprehensive telemetry collection for distributed Locust
load tests, capturing test lifecycle events, request statistics, and system metrics
for export to OpenTelemetry-compatible backends.
"""

import logging
from typing import Any, ClassVar, Dict, Optional

import gevent
from locust.env import Environment

from locust_telemetry.core.recorder import TelemetryBaseRecorder
from locust_telemetry.recorders.otel.metrics import OtelMetricsDefinition
from locust_telemetry.recorders.otel.mixins import LocustOtelCommonRecorderMixin

logger = logging.getLogger(__name__)


class MasterLocustOtelRecorder(LocustOtelCommonRecorderMixin, TelemetryBaseRecorder):
    """
    OpenTelemetry metrics recorder implementation for Locust MasterRunner.

    Collects and exports comprehensive telemetry data including test lifecycle events,
    request statistics, and system performance metrics to OpenTelemetry backends.

    Responsibilities
    ----------------
    - Capture test lifecycle events (start, stop, spawning completion)
    - Record aggregate and per-endpoint request statistics
    - Monitor and export system resource utilization metrics
    - Manage background metric collection processes
    - Enrich all metrics with contextual metadata (run_id, testplan, etc.)

    Configuration
    -------------
    Configured via Locust environment variables and command-line options.
    Metrics are exported through the configured OpenTelemetry SDK exporter.

    Notes
    -----
    - Exclusive to master nodes in distributed Locust deployments
    - Requires psutil for system-level metric collection
    - Metrics collection interval configurable via lt_stats_recorder_interval
    """

    name: ClassVar[str] = "master_otel_recorder"

    def __init__(self, env: Environment) -> None:
        """
        Initialize the OpenTelemetry recorder for master node telemetry collection.

        Parameters
        ----------
        env : Environment
            The Locust environment instance providing access to runner state,
            statistics, and event hooks for metric collection.
        """
        super().__init__(env)
        self._request_stats_recorder: Optional[gevent.Greenlet] = None
        self.metrics: Optional[OtelMetricsDefinition] = None

        # Register event listeners for test lifecycle and OpenTelemetry configuration
        env.events.init.add_listener(self.configure_otel)
        env.events.test_start.add_listener(self.on_test_start)
        env.events.test_stop.add_listener(self.on_test_stop)
        env.events.spawning_complete.add_listener(self.on_spawning_complete)

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle test initiation event and initialize metric collection processes.

        Executes upon test commencement to:
        - Record test start telemetry events
        - Initialize background metric collection greenlet
        - Establish periodic statistics recording

        Notes
        -----
        Inherits and extends base class test start functionality for
        comprehensive metric collection setup.
        """
        logger.info("[otel] Initializing OpenTelemetry metrics collection")
        super().on_test_start(*args, **kwargs)

        # Record test initiation events
        event_attributes = self._get_event_attributes("test_start")
        self.metrics.events.test_start_event.record(
            self.now_ms, attributes=event_attributes
        )
        self.metrics.events.test_event.record(self.now_ms, attributes=event_attributes)

        # Launch background statistics collection process
        self._request_stats_recorder = gevent.spawn(self._start_recording_request_stats)

        logger.info(
            "[otel] Test initiated - OpenTelemetry metrics collection active",
            extra=self.recorder_context(),
        )

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle test termination event and finalize metric collection.

        Executes upon test completion to:
        - Terminate background collection processes
        - Record final test stop events
        - Ensure complete metric flush before termination

        Notes
        -----
        Guarantees comprehensive final metric collection before test termination.
        """
        super().on_test_stop(*args, **kwargs)

        self._stop_recording_request_stats()

        # Record test completion events
        stop_attributes = self._get_event_attributes("test_stop")
        self.metrics.events.test_stop_event.record(
            self.now_ms, attributes=stop_attributes
        )
        self.metrics.events.test_event.record(self.now_ms, attributes=stop_attributes)

        logger.info(
            "[otel] Test completed - final metrics recorded and exported",
            extra=self.recorder_context(),
        )

    def on_spawning_complete(self, user_count: int) -> None:
        """
        Handle user spawning completion event.

        Parameters
        ----------
        user_count : int
            The total number of successfully spawned virtual users.

        Records spawning completion metrics and updates user count telemetry
        to reflect the stabilized user load.
        """
        spawn_attributes = {
            **self.recorder_context(),
            "user_count": str(user_count),
            "event_type": "spawning_complete",
        }

        self.metrics.events.spawn_complete_event.record(
            self.now_ms, attributes=spawn_attributes
        )
        self.metrics.events.test_event.record(self.now_ms, attributes=spawn_attributes)

        logger.info(
            f"[otel] User spawning completed - {user_count} virtual users active",
            extra=self.recorder_context(),
        )

    def record_request_stats(self) -> None:
        """
        Record comprehensive request statistics metrics.

        Collects and exports:
        - Aggregate request counts and error rates
        - Current active user count
        - Response time distribution metrics
        """
        stats = self.env.stats.total
        attributes = self.recorder_context()

        # Record user count and aggregate request metrics
        self.metrics.requests.user_count.add(
            self.env.runner.user_count, attributes=attributes
        )
        self.metrics.requests.requests_counter.add(
            stats.num_requests, attributes=attributes
        )
        self.metrics.requests.errors_counter.add(
            stats.num_failures, attributes=attributes
        )

        # Record response time distribution if available
        if stats.num_requests > 0:
            self.metrics.requests.request_duration.record(
                stats.avg_response_time, attributes=attributes
            )

    def record_endpoint_success_stats(self) -> None:
        """
        Record per-endpoint successful request metrics.

        Iterates through all tracked endpoints to export granular success rates
        and request volumes for detailed performance analysis.
        """
        endpoint_count = 0
        for (endpoint_name, http_method), stats in self.env.stats.entries.items():
            endpoint_attributes = {
                **self.recorder_context(),
                "endpoint": endpoint_name,
                "http_method": http_method,
            }
            self.metrics.requests.endpoint_success_counter.add(
                stats.num_requests, attributes=endpoint_attributes
            )
            endpoint_count += 1

        logger.debug(
            f"[otel] Recorded success metrics for {endpoint_count} endpoints",
            extra=self.recorder_context(),
        )

    def record_endpoint_error_stats(self) -> None:
        """
        Record per-endpoint error statistics and failure metrics.

        Provides detailed error breakdown by endpoint and error type for
        comprehensive failure analysis and debugging.
        """
        error_count = 0
        for error_key, error in self.env.stats.errors.items():
            error_attributes = {
                **self.recorder_context(),
                "error_type": error.error,
                "endpoint": error.name,
                "http_method": error.method,
            }
            self.metrics.requests.endpoint_errors_counter.add(
                error.occurrences, attributes=error_attributes
            )
            error_count += 1

        logger.debug(
            f"[otel] Recorded error metrics for {error_count} error types",
            extra=self.recorder_context(),
        )

    def _start_recording_request_stats(self) -> None:
        """
        Background process for periodic request statistics collection.

        Continuously collects and exports request metrics at configured intervals
        until explicitly terminated during test completion.

        Notes
        -----
        Execution interval controlled by lt_stats_recorder_environment option.
        Gracefully handles termination signals for clean shutdown.
        """
        logger.info("[otel] Initiating background request statistics collection")
        try:
            collection_interval = self.env.parsed_options.lt_stats_recorder_interval
            while True:
                self.record_request_stats()
                gevent.sleep(collection_interval)
        except gevent.GreenletExit:
            logger.info("[otel] Request statistics collection terminated gracefully")

    def _stop_recording_request_stats(self) -> None:
        """
        Terminate background statistics collection and record final metrics.

        Ensures comprehensive final metric collection before terminating
        all background processes for clean shutdown.
        """
        logger.info("[otel] Terminating statistics collection processes")

        if self._request_stats_recorder:
            self._request_stats_recorder.kill()
            self._request_stats_recorder = None

        # Record comprehensive final metrics snapshot
        self.record_request_stats()
        self.record_endpoint_success_stats()
        self.record_endpoint_error_stats()

        logger.info("[otel] Final metrics recorded and collection processes terminated")

    def _get_event_attributes(self, event_type: str) -> Dict[str, str]:
        """
        Generate standardized attributes for event metrics.

        Parameters
        ----------
        event_type : str
            The type of event being recorded (e.g., 'test_start', 'test_stop')

        Returns
        -------
        Dict[str, str]
            Dictionary of attributes enriched with event context and metadata.
        """
        return {**self.recorder_context(), "event_type": event_type}
