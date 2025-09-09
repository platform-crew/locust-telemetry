"""
Centralized manager for Telemetry setup and lifecycle.

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


# ---------------------------------------------
# Plugin Management
# ---------------------------------------------
class PluginManager:
    """
    Singleton class that manages telemetry plugin registration and lifecycle.

    Responsibilities
    ----------------
    - Register plugins
    - Load plugins safely as per TelemetryManager's request
    """

    _instance: PluginManager | None = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.debug("[PluginManager] Creating singleton instance")
        return cls._instance

    def __init__(self):
        """Initialize the plugin manager and prepare the plugin registry."""
        if self._initialized:
            return
        self._plugins: List[BaseTelemetryPlugin] = []
        self._initialized = True

    @property
    def plugins(self):
        return self._plugins

    def register_plugin(self, plugin: BaseTelemetryPlugin) -> None:
        """
        Register a telemetry plugin to be loaded during test start.

        Parameters
        ----------
        plugin : BaseTelemetryPlugin
            The plugin instance to register.
        """
        if plugin not in self._plugins:
            self._plugins.append(plugin)
            logger.debug(
                f"[PluginManager] Plugin registered: {plugin.__class__.__name__}"
            )
        else:
            logger.warning(f"Plugin: {plugin.__class__.__name__} already registered")

    def load_plugins(self, environment: Environment, **kwargs: Any) -> None:
        """
        Load all registered plugins as per TelemetryManager's request. TelemetryManager
        decides when to load the plugins.

        TelemetryManager initiates the load_plugins during locust init event fire.

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        **kwargs : Any
            Additional keyword arguments passed by the event system.
        """
        for plugin in self._plugins:
            try:
                plugin.load(environment=environment, **kwargs)
                logger.info(f"Plugin [{plugin.__class__.__name__}] loaded successfully")
            except Exception:
                logger.exception(
                    f"Failed to load plugin [{plugin.__class__.__name__}] in "
                    f"{environment.runner.__class__.__name__}"
                )


# ---------------------------------------------
# Core Telemetry Orchestration
# ---------------------------------------------
class TelemetryManager:
    """
    Singleton class that manages core telemetry features such as logging, CLI arguments,
    test metadata, and worker communication.

    Responsibilities
    ----------------
    - Add CLI arguments for telemetry configuration.
    - Configure logging for master and worker processes.
    - Setup and propagate test metadata between master and workers.
    - Register worker message handlers to receive metadata.
    - Load plugins registered in PluginManager
    """

    _instance: TelemetryManager | None = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.debug("[TelemetryManager] Creating singleton instance")
        return cls._instance

    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager or PluginManager()

    def initialize(self) -> None:
        """
        Hook into Locust lifecycle events in the correct order:

        1. Add CLI arguments
        2. Setup logging
        3. Register worker metadata handlers
        4. Load registered plugins
        5. Setup metadata at test start
        6. Cleanup metadata at test stop
        """
        if self._initialized:
            return

        events.init_command_line_parser.add_listener(self._add_arguments)
        events.init.add_listener(self._setup_logging)
        events.init.add_listener(self._register_metadata_handler)
        events.init.add_listener(self.plugin_manager.load_plugins)
        events.test_start.add_listener(self._setup_metadata)

        self._initialized = True

        logger.debug("[TelemetryManager] Initialized and hooks registered")

    # -------------------------------
    # Event Handlers
    # -------------------------------
    def _add_arguments(self, parser: LocustArgumentParser) -> None:
        """
        Add core telemetry CLI arguments to the Locust argument parser.

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

        # Load and parse env variables per plugin
        for p in self.plugin_manager.plugins:
            p.add_arguments(parser)

    def _setup_logging(self, environment: Environment, **kwargs: Any) -> None:
        """
        Configure logging for the current process.

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        """
        configure_logging()
        logger.info(
            f"[{environment.runner.__class__.__name__}] Logging configured successfully"
        )

    def _register_metadata_handler(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Register worker message handler to receive test metadata.

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        """
        if isinstance(environment.runner, WorkerRunner):
            environment.runner.register_message(
                "set_metadata",
                lambda msg, **kw: apply_worker_metadata(environment, msg.data),
            )
            logger.info("[Worker] Metadata handler registered successfully")

    def _setup_metadata(self, environment: Environment, **kwargs: Any) -> None:
        """
        Setup test metadata at test start.

        - Master sends metadata to all workers.

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
