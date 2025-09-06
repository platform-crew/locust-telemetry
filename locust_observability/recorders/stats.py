"""
Master Node Stats Recorder

This module provides the `MasterNodeStatsRecorder` class, which runs on the
Locust master node. It captures lifecycle events and request statistics, logging
them in a format suitable for observability tools.

The recorder listens to:
- test_start
- test_stop
- spawning_complete

It periodically logs request statistics to the console and final
aggregated stats at test end.
"""

import logging
import os
import socket
import time
from typing import Any, ClassVar, Dict, Optional

import gevent
from locust.env import Environment

from locust_observability.recorders.base import BaseRecorder
from locust_observability.metrics import MetricsEnum, EventsEnum

logger = logging.getLogger(__name__)


class MasterNodeStatsRecorder(BaseRecorder):
    """
    Recorder for Locust master node.

    This recorder captures:
    - Lifecycle events (test start/stop, spawning complete)
    - Aggregate and per-endpoint request statistics
    - Error statistics

    The recorder spawns a background greenlet to log request stats periodically.

    Attributes:
        name (ClassVar[str]): Identifier for the recorder.
    """

    name: ClassVar[str] = "master_recorder"

    def __init__(self, env: Environment) -> None:
        """
        Initialize the master node stats recorder.

        Args:
            env (Environment): The Locust environment instance.
        """
        super().__init__(env)
        self._username: str = os.getenv("USER", "unknown")
        self._hostname: str = socket.gethostname()
        self._pid: int = os.getpid()
        self._request_stats_logger: Optional[gevent.Greenlet] = None

        # Register master-only event listeners
        env.events.test_start.add_listener(self.on_test_start)
        env.events.test_stop.add_listener(self.on_test_stop)
        env.events.spawning_complete.add_listener(self.on_spawning_complete)

    # --- Event Handlers ---

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        Handler called when a test starts.

        Spawns the background logger greenlet and logs the test start event.
        """
        self._request_stats_logger = gevent.spawn(self._log_request_stats)
        self.log_metrics(
            metric=EventsEnum.TEST_START_EVENT.value,
            num_clients=self.env.parsed_options.num_users,
            profile_name=self.env.parsed_options.profile,
            username=self._username,
        )

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Handler called when a test stops.

        Stops background logging, logs final stats and errors, and emits the test stop event.

        Args:
            *args: Positional arguments passed by Locust.
            **kwargs: Keyword arguments passed by Locust.
        """
        self._stop_request_stats_logger()
        self._log_total_stats(final=True)
        self._log_entry_stats()
        self._log_error_stats()
        time.sleep(self.env.parsed_options.wait_after_test_stop)
        self.log_metrics(
            metric=EventsEnum.TEST_STOP_EVENT.value,
            text=f"{self.env.parsed_options.testplan} finished. Stopping the tests.",
        )

    def on_spawning_complete(self, user_count: int) -> None:
        """
        Handler called when user ramp-up is complete.

        Args:
            user_count (int): Number of users spawned.
        """
        self.log_metrics(
            metric=EventsEnum.SPAWN_COMPLETE_EVENT.value,
            user_count=user_count,
            text=(
                f"{self.env.parsed_options.testplan} ramp-up complete, "
                f"{user_count} users spawned"
            ),
        )

    # --- Helpers ---

    def _get_stats(self, st: Any) -> Dict[str, Any]:
        """
        Convert Locust stats object to a dictionary suitable for observability tools.

        Args:
            st: A Locust stats object (total, entry, or error).

        Returns:
            Dict[str, Any]: Locust stats dict with 95th and 99th percentiles.
        """
        stats = st.to_dict()
        stats["percentile_95"] = stats.pop("response_time_percentile_0.95", "")
        stats["percentile_99"] = stats.pop("response_time_percentile_0.99", "")
        return stats

    def _stop_request_stats_logger(self) -> None:
        """Stop the background request stats logger greenlet, if running."""
        if self._request_stats_logger:
            self._request_stats_logger.kill()
            self._request_stats_logger = None

    def _log_total_stats(self, final: bool = False) -> None:
        """
        Log aggregated request statistics.

        Args:
            final (bool): Indicates if it's a periodic log or final log on test stop.
        """
        metric = (
            MetricsEnum.REQUEST_FINAL_STATS_METRIC.value
            if final
            else MetricsEnum.REQUEST_CURRENT_STATS_METRIC.value
        )
        self.log_metrics(
            metric=metric,
            user_count=self.env.runner.user_count,
            **self._get_stats(self.env.stats.total),
        )

    def _log_entry_stats(self) -> None:
        """Log per-endpoint request statistics."""
        for (url, method), stats in self.env.stats.entries.items():
            self.log_metrics(
                metric=MetricsEnum.REQUEST_ENDPOINT_STATS_METRIC.value,
                request_path=url,
                **self._get_stats(stats),
            )

    def _log_error_stats(self) -> None:
        """Log per-endpoint error statistics."""
        for key, error in self.env.stats.errors.items():
            self.log_metrics(
                metric=MetricsEnum.REQUEST_ENDPOINT_ERRORS_METRIC.value,
                **self._get_stats(error),
            )

    def _log_request_stats(self) -> None:
        """
        Background loop that continuously logs current request stats.

        Runs until the greenlet is killed or the test ends.
        """
        try:
            while True:
                if not self.env.runner:
                    return
                self._log_total_stats(final=False)
                gevent.sleep(self.env.parsed_options.recorder_interval)
        except gevent.GreenletExit:
            logger.info("Request stats logger stopped cleanly")
