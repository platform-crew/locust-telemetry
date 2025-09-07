"""
Kubernetes Telemetry Plugin for Locust
======================================

This module defines the `K8TelemetryPlugin`, a telemetry plugin for
collecting Kubernetes metrics during Locust load tests.

Responsibilities
----------------
- Register plugin-specific CLI arguments and environment variables.
- Initialize master and worker telemetry recorders.
- Integrate with the core `TelemetryPluginManager` for lifecycle management.

Functions
---------
k8_plugin_load(*args, **kwargs)
    Load and register the Kubernetes telemetry plugin with Locust.
"""

import logging
from typing import Any

from locust.argument_parser import LocustArgumentParser
from locust.env import Environment

from locust_telemetry import config
from locust_telemetry.core.manager import TelemetryPluginManager
from locust_telemetry.core.plugin import BaseTelemetryPlugin

logger = logging.getLogger(__name__)


class K8TelemetryPlugin(BaseTelemetryPlugin):
    """
    Telemetry plugin for Kubernetes metrics.

    Inherits from `BaseTelemetryPlugin` and provides hooks for:
    - Adding plugin-specific CLI arguments
    - Registering master and worker telemetry recorders
    """

    def add_arguments(self, parser: LocustArgumentParser) -> None:
        """
        Add CLI arguments and environment variables for the K8 telemetry plugin.

        Args:
            parser (LocustArgumentParser): The Locust argument parser.
        """
        group = parser.add_argument_group(
            "telemetry.k8 - Locust Metrics",
            "Environment variables for Kubernetes telemetry plugin",
        )
        group.add_argument(
            "--k8-telemetry-recorder-interval",
            type=int,
            help="Interval (seconds) for Kubernetes metrics recorder updates.",
            env_var="K8_TELEMETRY_RECORDER_INTERVAL",
            default=config.DEFAULT_RECORDER_INTERVAL,
        )

    def register_master_telemetry_recorder(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Register master-specific telemetry recorder.

        Args:
            environment (Environment): Locust environment.
            **kwargs: Additional arguments.
        """
        pass

    def register_worker_telemetry_recorder(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Register worker-specific telemetry recorder.

        Args:
            environment (Environment): Locust environment.
            **kwargs: Additional arguments.
        """
        pass


def k8_plugin_load(*args, **kwargs) -> None:
    """
    Initialize and register the Kubernetes telemetry plugin with Locust.

    This function can be called at the start of your Locust test script
    to ensure the plugin is loaded and lifecycle hooks are registered.

    Args:
        *args: Positional arguments.
        **kwargs: Keyword arguments.
    """
    manager = TelemetryPluginManager()
    manager.register_plugin(plugin=K8TelemetryPlugin())
