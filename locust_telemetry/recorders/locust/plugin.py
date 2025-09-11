"""
Locust Telemetry Recorder Plugin
--------------------------------

This module defines the `LocustTelemetryRecorderPlugin`, which integrates
telemetry recording into Locust runs. It initializes master and
worker telemetry recorders to capture lifecycle events, request
statistics, and worker system metrics.

Responsibilities
----------------
- Register CLI arguments for telemetry configuration.
- Register master and worker telemetry recorders.
- Initialize telemetry via TelemetryRecorderPluginManager.
"""

import logging
from typing import Any

from locust.env import Environment

from locust_telemetry import config
from locust_telemetry.core.manager import telemetry_recorder_plugin
from locust_telemetry.core.plugin import TelemetryRecorderPluginBase
from locust_telemetry.recorders.locust.master import MasterLocustTelemetryRecorder
from locust_telemetry.recorders.locust.worker import WorkerLocustTelemetryRecorder

logger = logging.getLogger(__name__)


@telemetry_recorder_plugin
class LocustTelemetryRecorderPlugin(TelemetryRecorderPluginBase):
    """
    Core telemetry recorder plugin for Locust.

    Responsibilities
    ----------------
    - Register CLI arguments for telemetry configuration.
    - Load master-side telemetry recorders.
    - Load worker-side telemetry recorders.
    """

    RECORDER_PLUGIN_ID = config.TELEMETRY_STATS_RECORDER_PLUGIN_ID

    def add_cli_arguments(self, group: Any) -> None:
        """
        Register CLI arguments for this telemetry recorder plugin.

        Parameters
        ----------
        group : Any (_ArgumentGroup)
            The argument group to which telemetry recorder options are added.
        """
        group.add_argument(
            "--lt-stats-recorder-interval",
            type=int,
            help="Interval (in seconds) for telemetry statistics recorder updates.",
            env_var="LOCUST_TELEMETRY_STATS_RECORDER_INTERVAL",
            default=config.DEFAULT_STATS_RECORDER_INTERVAL,
        )
        group.add_argument(
            "--lt-system-usage-recorder-interval",
            type=int,
            help="Interval (in seconds) for system usage monitoring.",
            env_var="LOCUST_TELEMETRY_SYSTEM_USAGE_RECORDER_INTERVAL",
            default=config.DEFAULT_SYSTEM_USAGE_RECORDER_INTERVAL,
        )

    def load_master_telemetry_recorders(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Register the master-side telemetry recorder(s).

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        **kwargs : Any
            Additional context passed by the TelemetryCoordinator.
        """
        MasterLocustTelemetryRecorder(env=environment)

    def load_worker_telemetry_recorders(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Register the worker-side telemetry recorder(s).

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        **kwargs : Any
            Additional context passed by the TelemetryCoordinator.
        """
        WorkerLocustTelemetryRecorder(env=environment)
