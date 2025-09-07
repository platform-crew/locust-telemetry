"""
Master Node Locust Telemetry Recorder
=====================================

This module provides the `MasterLocustTelemetryRecorder` class, which runs on
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
import os
import socket
from typing import Any, ClassVar, Dict, Optional

import gevent
from locust.env import Environment

from locust_telemetry.core.telemetry import BaseTelemetryRecorder
from locust_telemetry.core_telemetry.constants import LocustTestEvent, RequestMetric

logger = logging.getLogger(__name__)


class MasterLocustTelemetryRecorder(BaseTelemetryRecorder):
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

    name: ClassVar[str] = "master_locust_telemetry_recorder"

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
        Handle the test_start event.

        Starts the background stats logger and emits the test start telemetry.
        """
        self._request_stats_logger = gevent.spawn(self._log_request_stats)
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
        self._stop_request_stats_logger()
        self._log_total_stats(final=True)
        self._log_entry_stats()
        self._log_error_stats()
        self.log_telemetry(
            telemetry=LocustTestEvent.STOP.value,
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

    # --- Helpers ---

    def _get_stats(self, st: Any) -> Dict[str, Any]:
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

    def _stop_request_stats_logger(self) -> None:
        """Stop the background request stats logger greenlet, if running."""
        if self._request_stats_logger:
            self._request_stats_logger.kill()
            self._request_stats_logger = None

    def _log_total_stats(self, final: bool = False) -> None:
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
            **self._get_stats(self.env.stats.total),
        )

    def _log_entry_stats(self) -> None:
        """Log per-endpoint request statistics."""
        for (url, method), stats in self.env.stats.entries.items():
            self.log_telemetry(
                telemetry=RequestMetric.ENDPOINT_STATS.value,
                request_path=url,
                **self._get_stats(stats),
            )

    def _log_error_stats(self) -> None:
        """Log per-endpoint error statistics."""
        for key, error in self.env.stats.errors.items():
            self.log_telemetry(
                telemetry=RequestMetric.ENDPOINT_ERRORS.value,
                **self._get_stats(error),
            )

    def _log_request_stats(self) -> None:
        """
        Background loop that logs current request stats
        at the configured telemetry recorder interval.
        """
        try:
            while True:
                if not self.env.runner:
                    return
                self._log_total_stats(final=False)
                gevent.sleep(self.env.parsed_options.locust_telemetry_recorder_interval)
        except gevent.GreenletExit:
            logger.info("Request stats logger stopped cleanly")
