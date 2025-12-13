"""Entry point for initializing telemetry in a Locust test run."""

import logging

from locust_telemetry.core.coordinator import TelemetryCoordinator
from locust_telemetry.core.manager import RecorderPluginManager
from locust_telemetry.recorders.json.plugin import (
    LocustJsonRecorderPlugin,
)
from locust_telemetry.recorders.otel.plugin import (
    LocustOtelRecorderPlugin,
)

logger = logging.getLogger(__name__)


CONFIGURED_RECORDER_PLUGINS = (
    # Locust stats recorder.
    LocustJsonRecorderPlugin,
    # Locust otel
    LocustOtelRecorderPlugin,
)


def initialize(*args, **kwargs) -> None:
    """
    Register all the available plugins and start the coordinator.

    For autodiscovery use only. Manual users should call `setup_telemetry()`.
    """
    recorder_plugin_manager = RecorderPluginManager()
    for plugin_cls in CONFIGURED_RECORDER_PLUGINS:
        recorder_plugin_manager.register_recorder_plugin(plugin_cls())

    coordinator = TelemetryCoordinator(recorder_plugin_manager=recorder_plugin_manager)
    coordinator.initialize()


def setup_telemetry() -> None:
    """
    High-level convenience initializer.

    Since Locust doesn’t have auto-discovery for plugins yet,
    this explicitly configures CLI args and initializes telemetry.
    """
    initialize()
