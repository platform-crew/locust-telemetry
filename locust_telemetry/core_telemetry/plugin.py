"""
This module defines the `LocustTelemetryPlugin`, which integrates
telemetry recording into Locust runs. It initializes master and
worker telemetry recorders to capture lifecycle events, request
statistics, and worker system metrics.

Responsibilities
----------------
- Add CLI arguments for telemetry configuration.
- Register master and worker telemetry recorders.
"""

import logging
from typing import Any

from locust.argument_parser import LocustArgumentParser
from locust.env import Environment

from locust_telemetry import config
from locust_telemetry.core.manager import PluginManager, TelemetryManager
from locust_telemetry.core.plugin import BaseTelemetryPlugin
from locust_telemetry.core_telemetry.master import MasterLocustTelemetryRecorder
from locust_telemetry.core_telemetry.worker import WorkerLocustTelemetryRecorder

logger = logging.getLogger(__name__)


class LocustTelemetryPlugin(BaseTelemetryPlugin):
    """
    Plugin for enabling telemetry in Locust.

    Responsibilities
    ----------------
    - Add CLI arguments for telemetry configuration.
    - Register master and worker telemetry recorders.
    """

    def add_arguments(self, parser: LocustArgumentParser) -> None:
        """
        Register CLI arguments for telemetry configuration.

        Args
        ----
        parser : LocustArgumentParser
            The Locust argument parser instance.
        """
        group = parser.add_argument_group(
            "telemetry.locust - Locust Telemetry",
            "Environment variables for configuring the telemetry plugin",
        )
        group.add_argument(
            "--locust-telemetry-recorder-interval",
            type=int,
            help="Interval (seconds) for telemetry recorder updates.",
            env_var="LOCUST_TELEMETRY_RECORDER_INTERVAL",
            default=config.DEFAULT_RECORDER_INTERVAL,
        )

    def load_master_telemetry_recorders(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Register the telemetry recorder for the master node.

        Args
        ----
        environment : Environment
            The Locust environment instance.
        """
        MasterLocustTelemetryRecorder(env=environment)

    def load_worker_telemetry_recorders(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Register the telemetry recorder for worker nodes.

        Args
        ----
        environment : Environment
            The Locust environment instance.
        """
        WorkerLocustTelemetryRecorder(env=environment)


def entry_point(*args, **kwargs):
    """
    Initialize and register the core telemetry plugin with Locust.

    This function sets up the telemetry system by:

    1. Creating or retrieving the singleton `PluginManager`.
    2. Registering the core `LocustTelemetryPlugin`.
    3. Initializing the singleton `TelemetryManager` with the plugin manager,
       which hooks into Locust lifecycle events (CLI arguments, logging,
       metadata handling, plugin loading).

    Usage:
        Call this function at the start of your Locust test script to ensure
        telemetry is initialized before any load tests begin.

    Parameters
    ----------
    *args : tuple
        Optional positional arguments, currently unused.
    **kwargs : dict
        Optional keyword arguments, currently unused.
    """
    plugin_manager = PluginManager()
    plugin_manager.register_plugin(plugin=LocustTelemetryPlugin())
    telemetry_manager = TelemetryManager(plugin_manager=plugin_manager)
    telemetry_manager.initialize()
