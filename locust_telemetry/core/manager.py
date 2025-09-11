"""
Recorder manager for Locust Telemetry.

Responsibilities
----------------
- Maintain a registry of telemetry recorder plugins.
- Provide a singleton manager (one per process).
- Allow safe recorder plugin registration (avoiding duplicates).
- Load and activate recorder plugins according to user configuration.
"""

from __future__ import annotations

import logging
from typing import Any, List

from locust.env import Environment

from locust_telemetry.core.plugin import TelemetryRecorderPluginBase

logger = logging.getLogger(__name__)


class TelemetryRecorderPluginManager:
    """
    Singleton class that manages telemetry recorder plugin registration and loading.

    Responsibilities
    ----------------
    - Register recorder plugins provided by extensions.
    - Maintain a central recorder plugin registry per process.
    - Safely load recorder plugins when requested by the orchestrator.
    """

    _instance: TelemetryRecorderPluginManager | None = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.debug("[TelemetryRecorderPluginManager] Creating singleton instance")
        return cls._instance

    def __init__(self):
        """Initialize the recorder plugin registry if not already initialized."""
        if self._initialized:
            return
        self._recorder_plugins: List[TelemetryRecorderPluginBase] = []
        self._initialized = True

    @property
    def recorder_plugins(self) -> List[TelemetryRecorderPluginBase]:
        """
        Return the list of registered recorder plugins.

        Returns
        -------
        List[TelemetryRecorderPluginBase]
            The currently registered recorder plugin instances.
        """
        return self._recorder_plugins

    def register_recorder_plugin(self, plugin: TelemetryRecorderPluginBase) -> None:
        """
        Register a telemetry recorder plugin for later loading.

        Parameters
        ----------
        plugin : TelemetryRecorderPluginBase
            The recorder plugin instance to register.
        """
        if plugin not in self._recorder_plugins:
            self._recorder_plugins.append(plugin)
            logger.debug(
                f"[TelemetryRecorderPluginManager] Recorder plugin registered: "
                f"{plugin.__class__.__name__}"
            )
        else:
            logger.warning(
                f"[TelemetryRecorderPluginManager] Recorder plugin already registered: "
                f"{plugin.__class__.__name__}"
            )

    def load_recorder_plugins(self, environment: Environment, **kwargs: Any) -> None:
        """
        Load all registered recorder plugins.

        This method is typically invoked by ``TelemetryOrchestrator`` during
        Locust's init phase. Each recorder plugin receives the current
        environment and optional event context.

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        **kwargs : Any
            Additional context passed by the event system.
        """
        enabled_plugins = getattr(
            environment.parsed_options, "enable_telemetry_plugin", None
        )

        if not enabled_plugins:
            logger.info(
                "No telemetry recorder plugin enabled. Use '--enable-telemetry-plugin' "
                "to activate one or more plugins."
            )
            return

        for plugin in self._recorder_plugins:
            if plugin.RECORDER_PLUGIN_ID not in enabled_plugins:
                continue

            try:
                plugin.load(environment=environment, **kwargs)
                logger.info(
                    f"[TelemetryRecorderPluginManager] Recorder plugin loaded "
                    f"successfully: {plugin.__class__.__name__}"
                )
            except Exception:
                logger.exception(
                    f"[TelemetryRecorderPluginManager] Failed to load recorder plugin: "
                    f"{plugin.__class__.__name__} "
                    f"in {environment.runner.__class__.__name__}. "
                    f"Enabled recorder plugins: {enabled_plugins}"
                )


def telemetry_recorder_plugin(cls):
    """
    Class decorator to register a telemetry recorder plugin automatically.

    Usage
    -----
    @telemetry_recorder_plugin
    class MyRecorderPlugin(TelemetryRecorderPluginBase):
        ...
    """
    manager = TelemetryRecorderPluginManager()
    manager.register_recorder_plugin(cls())
    return cls
