"""
Locust Telemetry Plugin

This module defines the `LocustTelemetryPlugin`, which integrates
telemetry recording into Locust runs. It initializes master and
worker telemetry recorders to capture lifecycle events, request
statistics, and worker system metrics.

The plugin:
- Adds CLI arguments for telemetry configuration
- Registers master and worker telemetry recorders
"""

import logging
from typing import Any

from locust.argument_parser import LocustArgumentParser
from locust.env import Environment

from locust_telemetry import config
from locust_telemetry.core.manager import TelemetryPluginManager
from locust_telemetry.core.plugin import BaseTelemetryPlugin
from locust_telemetry.core_telemetry.stats import MasterLocustTelemetryRecorder
from locust_telemetry.core_telemetry.system import WorkerLocustTelemetryRecorder

logger = logging.getLogger(__name__)


class LocustTelemetryPlugin(BaseTelemetryPlugin):
    """
    Plugin for enabling telemetry in Locust.

    Responsibilities:
    - Add CLI arguments for telemetry configuration
    - Register master and worker telemetry recorders
    """

    def add_arguments(self, parser: LocustArgumentParser) -> None:
        """
        Register CLI arguments for telemetry configuration.

        Args:
            parser (LocustArgumentParser): The Locust argument parser.
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

    def register_master_telemetry_recorder(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Register the telemetry recorder for the master node.

        Args:
            environment (Environment): The Locust environment instance.
        """
        MasterLocustTelemetryRecorder(env=environment)

    def register_worker_telemetry_recorder(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Register the telemetry recorder for worker nodes.

        Args:
            environment (Environment): The Locust environment instance.
        """
        WorkerLocustTelemetryRecorder(env=environment)


def core_plugin_load(*args, **kwargs):
    """
    Initialize and register the core telemetry plugin with Locust.

    This function can be called at the start of your test script
    to ensure the plugin is loaded and lifecycle hooks are registered.
    """

    manager = TelemetryPluginManager()
    manager.register_plugin(plugin=LocustTelemetryPlugin())
