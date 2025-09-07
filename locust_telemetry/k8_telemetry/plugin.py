import logging
from typing import Any

from locust.argument_parser import LocustArgumentParser
from locust.env import Environment

from locust_telemetry import config
from locust_telemetry.core.manager import TelemetryPluginManager
from locust_telemetry.core.plugin import BaseTelemetryPlugin

logger = logging.getLogger(__name__)


class K8TelemetryPlugin(BaseTelemetryPlugin):

    def add_arguments(self, parser: LocustArgumentParser) -> None:
        group = parser.add_argument_group(
            "telemetry.k8 - Locust Metrics",
            "Environment variables for locust metrics plugin",
        )
        group.add_argument(
            "--k8-telemetry-recorder-interval",
            type=int,
            help="Interval (seconds) for k8 metrics recorder updates.",
            env_var="k8_TELEMETRY_RECORDER_INTERVAL",
            default=config.DEFAULT_RECORDER_INTERVAL,
        )

    def register_master_telemetry_recorder(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        pass

    def register_worker_telemetry_recorder(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        pass


def k8_plugin_load(*args, **kwargs):
    """
    Initialize and register the K8 telemetry plugin with Locust.

    This function can be called at the start of your test script
    to ensure the plugin is loaded and lifecycle hooks are registered.
    """
    manager = TelemetryPluginManager()
    manager.register_plugin(plugin=K8TelemetryPlugin())
