"""
This module provides the `MasterLocustJsonTelemetryRecorder` class, which runs on
the Locust master node. It captures lifecycle events and request statistics,
logging them in a format suitable for observability tools.

Responsibilities
----------------
- Listen to test lifecycle events: `test_start`, `test_stop`, `spawning_complete`.
- Periodically log request statistics during the test.
- Output final aggregated stats at test end.
- Support observability tools integration.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, ClassVar, Dict, Optional

import gevent
from locust.env import Environment

from locust_telemetry.core.recorder import TelemetryBaseRecorder
from locust_telemetry.recorders.json.locust.constants import (
    TEST_STOP_BUFFER_FOR_GRAPHS,
    LocustTestEvent,
    RequestMetric,
)
from locust_telemetry.recorders.json.locust.mixins import (
    LocustJsonTelemetryCommonRecorderMixin,
)

logger = logging.getLogger(__name__)


class MasterLocustJsonTelemetryRecorder(
    LocustJsonTelemetryCommonRecorderMixin, TelemetryBaseRecorder
):
    """
    Telemetry recorder for the Locust master node.

    Responsibilities
    ----------------
    - Handle lifecycle events (test start/stop, spawning complete)
    - Collect aggregate and per-endpoint request statistics
    - Collect error statistics
    - Run a background greenlet to periodically log request stats

    Attributes
    ----------
    name : ClassVar[str]
        Identifier for the recorder.
    """

    name: ClassVar[str] = "master_json_recorder"

    def __init__(self, env: Environment) -> None:
        """
        Initialize the master telemetry recorder.

        Registers event listeners for test lifecycle events.

        Parameters
        ----------
        env : Environment
            The Locust environment instance.
        """
        super().__init__(env)
        self._request_stats_recorder: Optional[gevent.Greenlet] = None

        # Register master-only event listeners
        env.events.test_start.add_listener(self.on_test_start)
        env.events.test_stop.add_listener(self.on_test_stop)
        env.events.spawning_complete.add_listener(self.on_spawning_complete)

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle the test_start event.

        Starts the background stats logger and emits the test start telemetry.
        """
        super().on_test_start(*args, **kwargs)
        self._request_stats_recorder = gevent.spawn(self.start_recording_request_stats)
        self.log_telemetry(
            telemetry=LocustTestEvent.START.value,
            num_clients=self.env.parsed_options.num_users,
            profile_name=self.env.parsed_options.profile,
            username=self._username,
        )

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle the test_stop event.

        Stops background logging, logs final stats and errors,
        and emits the test stop telemetry.
        """
        super().on_test_stop(*args, **kwargs)
        self.stop_recording_request_stats()

        # Hack: For graphs to create autolink
        # Compute current UTC time + 2 seconds
        end_time = datetime.now(timezone.utc) + timedelta(
            seconds=TEST_STOP_BUFFER_FOR_GRAPHS
        )
        end_time_str = end_time.isoformat(timespec="milliseconds").replace(
            "+00:00", "Z"
        )

        self.log_telemetry(
            telemetry=LocustTestEvent.STOP.value,
            endtime=end_time_str,
            text=f"{self.env.parsed_options.testplan} finished. Stopping the tests.",
        )

    def on_spawning_complete(self, user_count: int) -> None:
        """
        Handle the spawning_complete event.

        Parameters
        ----------
        user_count : int
            Number of users spawned.
        """
        self.log_telemetry(
            telemetry=LocustTestEvent.SPAWN_COMPLETE.value,
            user_count=user_count,
            text=(
                f"{self.env.parsed_options.testplan} ramp-up complete, "
                f"{user_count} users spawned"
            ),
        )

    @staticmethod
    def stats_to_dict(st: Any) -> Dict[str, Any]:
        """
        Convert a Locust stats object to a dictionary for observability tools.

        Parameters
        ----------
        st : Any
            A Locust stats object (total, entry, or error).

        Returns
        -------
        Dict[str, Any]
            Stats dictionary including 95th and 99th percentiles.
        """
        stats = st.to_dict()
        stats["percentile_95"] = stats.pop("response_time_percentile_0.95", "")
        stats["percentile_99"] = stats.pop("response_time_percentile_0.99", "")
        return stats

    def log_request_stats(self, final: bool = False) -> None:
        """
        Log aggregated request statistics.

        Parameters
        ----------
        final : bool, optional
            True for final log on test stop, False for periodic logs.
        """
        telemetry = (
            RequestMetric.FINAL_STATS.value
            if final
            else RequestMetric.CURRENT_STATS.value
        )
        self.log_telemetry(
            telemetry=telemetry,
            user_count=self.env.runner.user_count,
            **self.stats_to_dict(self.env.stats.total),
        )

    def log_endpoint_success_stats(self) -> None:
        """Log endpoint success request statistics."""
        for (url, method), stats in self.env.stats.entries.items():
            self.log_telemetry(
                telemetry=RequestMetric.ENDPOINT_STATS.value,
                request_path=url,
                **self.stats_to_dict(stats),
            )

    def log_endpoint_error_stats(self) -> None:
        """Log endpoint error statistics."""
        for key, error in self.env.stats.errors.items():
            self.log_telemetry(
                telemetry=RequestMetric.ENDPOINT_ERRORS.value,
                **self.stats_to_dict(error),
            )

    def start_recording_request_stats(self) -> None:
        """
        Background loop that logs current request stats
        at the configured telemetry recorder interval.
        """
        try:
            while True:
                self.log_request_stats(final=False)
                gevent.sleep(self.env.parsed_options.lt_stats_recorder_interval)
        except gevent.GreenletExit:
            logger.info("Request stats logger stopped cleanly")

    def stop_recording_request_stats(self) -> None:
        """Stop the background request stats recorder greenlet, if running."""
        if self._request_stats_recorder:
            self._request_stats_recorder.kill()
            self._request_stats_recorder = None

        logger.info("Logging the final statistics in json")
        self.log_request_stats(final=True)
        self.log_endpoint_success_stats()
        self.log_endpoint_error_stats()
