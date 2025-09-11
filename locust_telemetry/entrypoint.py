"""
Locust Telemetry Entrypoint
--------------------------

Entry point for initializing telemetry in a Locust test run.
"""

import logging

from locust_telemetry.core.coordinator import TelemetryCoordinator
from locust_telemetry.core.manager import TelemetryRecorderPluginManager

logger = logging.getLogger(__name__)


def initialize(*args, **kwargs) -> None:
    """
    Register all the available plugins and start the coordinator.

    For autodiscovery use only. Manual users should call `setup_telemetry()`.
    """
    coordinator = TelemetryCoordinator(
        recorder_plugin_manager=TelemetryRecorderPluginManager()
    )
    coordinator.initialize()


def setup_telemetry() -> None:
    """
    High-level convenience initializer.

    Since Locust doesn’t have auto-discovery for plugins yet,
    this explicitly configures CLI args and initializes telemetry.
    """
    initialize()
