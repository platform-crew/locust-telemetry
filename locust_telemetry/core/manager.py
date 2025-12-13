"""Recorder manager for Locust Telemetry."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from locust.env import Environment

from locust_telemetry import config
from locust_telemetry.core.exceptions import (
    RecorderPluginAlreadyRegistered,
    RecorderPluginLoadError,
)
from locust_telemetry.core.plugin import BaseRecorderPlugin
from locust_telemetry.metadata import set_test_metadata

logger = logging.getLogger(__name__)


class RecorderPluginManager:
    """
    Singleton class that manages telemetry recorder plugin registration and loading.

    Responsibilities
    ----------------
    - Register recorder plugins provided by extensions.
    - Maintain a central recorder plugin registry per process.
    - Safely load recorder plugins when requested by the orchestrator.
    """

    _instance: RecorderPluginManager | None = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.debug("[RecorderPluginManager] Creating singleton instance")
        return cls._instance

    def __init__(self):
        """
        Initialize the plugin manager.

        Ensures that the plugin registry is created only once for the process.
        Subsequent instantiations will reuse the existing singleton instance.
        """
        if self._initialized:
            return
        self._recorder_plugins: List[BaseRecorderPlugin] = []
        self._initialized = True

    @property
    def recorder_plugins(self) -> List[BaseRecorderPlugin]:
        """
        Get the list of registered recorder plugins.

        Returns
        -------
        List[BaseRecorderPlugin]
            The currently registered recorder plugin instances.
        """
        return self._recorder_plugins

    def register_recorder_plugin(self, plugin: BaseRecorderPlugin) -> None:
        """
        Register a telemetry recorder plugin for later loading.

        A plugin will only be added once to prevent duplicate registration.

        Parameters
        ----------
        plugin : BaseRecorderPlugin
            The recorder plugin instance to register.
        """
        if plugin in self._recorder_plugins:
            raise RecorderPluginAlreadyRegistered(
                f"[RecorderPluginManager] Recorder plugin already registered: "
                f"{plugin.__class__.__name__}"
            )

        self._recorder_plugins.append(plugin)
        logger.debug(
            f"[RecorderPluginManager] Recorder plugin registered: "
            f"{plugin.__class__.__name__}"
        )

    def register_plugin_clis(self, group: Any) -> None:
        """
        Register CLI arguments for all recorder plugins.

        This method is typically invoked by ``TelemetryOrchestrator`` during
        Locust's ``init_command_line_parser`` phase. Each recorder plugin
        receives the locust-telemetry CLI argument group.

        Parameters
        ----------
        group : argparse._ArgumentGroup
            The Locust CLI argument group.
        """
        for plugin in self._recorder_plugins:
            plugin.add_cli_arguments(group)

    def register_plugin_metadata(self, environment: Environment) -> Dict:
        """
        Collect and register test metadata from all recorder plugins.

        This method aggregates metadata contributed by each registered
        recorder plugin, merges it into the default environment metadata,
        and sets it on the given Locust environment.

        Parameters
        ----------
        environment : Environment
            The Locust environment instance where the metadata will be stored.

        Returns
        -------
        Dict
            A dictionary containing the merged environment metadata,
            including contributions from all recorder plugins.
        """
        metadata = config.DEFAULT_ENVIRONMENT_METADATA
        for plugin in self._recorder_plugins:
            metadata.update(plugin.add_test_metadata())

        cleaned_metadata = {
            k: val() if callable(val) else val for k, val in metadata.items()
        }
        set_test_metadata(environment, cleaned_metadata)
        return cleaned_metadata

    def load_recorder_plugins(self, environment: Environment, **kwargs: Any) -> None:
        """
        Load and activate all registered recorder plugins.

        This method is typically invoked by ``TelemetryOrchestrator`` during
        Locust's ``init`` phase. Each recorder plugin receives the current
        environment and any additional context provided by the event system.

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        **kwargs : Any
            Additional context passed by the event system.

        Raises
        ------
        Exception
            Logs and propagates plugin load failures with context.
        """
        enabled_plugins = getattr(
            environment.parsed_options, "enable_telemetry_recorder", None
        )

        logger.info(
            "[RecorderPluginManager] Following recorders are enabled",
            extra={"recorders": enabled_plugins},
        )

        for plugin in self._recorder_plugins:
            if plugin.RECORDER_PLUGIN_ID not in enabled_plugins:
                continue

            try:
                plugin.load(environment=environment, **kwargs)
                logger.info(
                    f"[RecorderPluginManager] Recorder plugin loaded "
                    f"successfully: {plugin.__class__.__name__}"
                )
            except Exception as e:
                raise RecorderPluginLoadError(
                    f"Failed to load recorder plugin: {plugin.__class__.__name__}"
                ) from e
