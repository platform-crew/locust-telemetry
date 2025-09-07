"""
Locust Telemetry Plugin Manager
===============================

Centralized manager for Locust Telemetry setup and lifecycle.

Responsibilities
----------------
- Handle CLI arguments for core telemetry and plugins.
- Configure logging (master and worker).
- Manage test metadata propagation between master and workers.
- Register message handlers for worker communication.
- Load and activate registered telemetry plugins at test start.
- Ensure singleton initialization (one manager per process).
"""

from __future__ import annotations

import logging
from typing import Any, List

from locust import events
from locust.argument_parser import LocustArgumentParser
from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry.core.plugin import BaseTelemetryPlugin
from locust_telemetry.logger import configure_logging
from locust_telemetry.metadata import (
    apply_worker_metadata,
    get_test_metadata,
    set_test_metadata,
)

logger = logging.getLogger(__name__)


class TelemetryPluginManager:
    """
    Singleton manager that orchestrates core telemetry features.

    Responsibilities
    ----------------
    - Register CLI arguments for telemetry and plugins.
    - Configure logging once per process.
    - Set and propagate test metadata between master and workers.
    - Register worker message handlers for metadata.
    - Load and activate registered plugins at test start.
    """

    _instance: TelemetryPluginManager | None = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of the manager is ever created."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.debug("[TelemetryPluginManager] Creating singleton instance")
        return cls._instance

    def __init__(self) -> None:
        """Initialize the manager and prepare the plugin registry."""
        if self._initialized:
            return

        self._plugins: List[BaseTelemetryPlugin] = []

        # Hook into Locust events (only once)
        self._register_hooks()

        # Mark as initialized after hooks are registered
        self._initialized = True
        logger.debug(
            "[TelemetryPluginManager] Instance created and event hooks registered"
        )

    def _register_hooks(self) -> None:
        """
        Hook into Locust lifecycle events.
        Must be called once before Locust starts running.
        """
        events.init_command_line_parser.add_listener(self._on_init_command_line_parser)
        events.init.add_listener(self._on_init)
        events.init.add_listener(self._on_init_worker)
        events.test_start.add_listener(self._on_test_start)

        logger.debug("[TelemetryPluginManager] Initialization complete")

    # -------------------------------
    # Plugin Management
    # -------------------------------

    def register_plugin(self, plugin: BaseTelemetryPlugin) -> None:
        """
        Add a telemetry plugin to the manager.

        Plugins are loaded automatically at test start.

        Parameters
        ----------
        plugin : BaseTelemetryPlugin
            The plugin instance to register.
        """
        if plugin not in self._plugins:
            self._plugins.append(plugin)
            logger.debug(
                f"[TelemetryPluginManager] Plugin "
                f"registered: {plugin.__class__.__name__}"
            )

    # -------------------------------
    # Event Listeners
    # -------------------------------

    def _on_init_command_line_parser(self, parser: LocustArgumentParser) -> None:
        """
        Define CLI arguments for both core telemetry and registered plugins.

        Parameters
        ----------
        parser : LocustArgumentParser
            The Locust argument parser.
        """
        group = parser.add_argument_group(
            "locust-telemetry - Core",
            "Environment variables for configuring Locust Telemetry",
        )
        group.add_argument(
            "--testplan",
            type=str,
            help="Unique identifier for the test run or service under test.",
            env_var="LOCUST_TESTPLAN_NAME",
            required=True,
        )

        for plugin in self._plugins:
            logger.debug(
                f"[TelemetryPluginManager] Adding CLI args for "
                f"plugin: {plugin.__class__.__name__}"
            )
            plugin.add_arguments(parser)

    def _on_init(self, environment: Environment, **kwargs: Any) -> None:
        """Configure logging once Locust initializes."""
        configure_logging()
        logger.info(
            f"[{environment.runner.__class__.__name__}] Logging configured successfully"
        )

    def _on_init_worker(self, environment: Environment, **kwargs: Any) -> None:
        """Worker runner: register message handler to receive test metadata."""
        if isinstance(environment.runner, WorkerRunner):
            environment.runner.register_message(
                "set_metadata",
                lambda msg, **kw: apply_worker_metadata(environment, msg.data),
            )
            logger.info("[Worker] Metadata handler registered successfully")

    def _on_test_start(self, environment: Environment, **kwargs: Any) -> None:
        """
        Triggered when a test starts.

        Actions:
        - Master sends metadata to all workers.
        - All registered plugins are loaded.

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        """
        if isinstance(environment.runner, MasterRunner):
            set_test_metadata(environment)
            metadata = get_test_metadata(environment)
            logger.info(
                "Sending test metadata to workers", extra={"metadata": metadata}
            )
            environment.runner.send_message("set_metadata", metadata)

        for plugin in self._plugins:
            logger.info(
                f"[TelemetryPluginManager][{environment.runner.__class__.__name__}] "
                f"Loading plugin: {plugin.__class__.__name__}"
            )
            plugin.load(environment, **kwargs)
