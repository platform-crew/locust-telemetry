"""
Singleton coordinator responsible for coordinating telemetry lifecycle with Locust.

Responsibilities
----------------
- Setup and propagate test metadata between master and workers.
- Register worker message handlers to receive metadata from master.
- Load telemetry recorders via ``TelemetryRecorderPluginManager``.
- Ensure singleton initialization (one Coordinator per process).
"""

from __future__ import annotations

import logging
from typing import Any

from locust import events
from locust.argument_parser import LocustArgumentParser
from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry.core.cli import register_telemetry_cli_args
from locust_telemetry.core.manager import TelemetryRecorderPluginManager
from locust_telemetry.logger import configure_logging
from locust_telemetry.metadata import (
    apply_worker_metadata,
    get_test_metadata,
    set_test_metadata,
)

logger = logging.getLogger(__name__)


class TelemetryCoordinator:
    """
    Singleton responsible for coordinating telemetry lifecycle with Locust.

    Responsibilities
    ----------------
    - Setup and propagate test metadata between master and workers.
    - Register worker message handlers to receive metadata from master.
    - Load telemetry recorders via ``TelemetryRecorderPluginManager``.
    - Ensure singleton initialization (one coordinator per process).
    """

    _instance: TelemetryCoordinator | None = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.debug("[TelemetryCoordinator] Creating singleton instance")
        return cls._instance

    def __init__(self, recorder_plugin_manager: TelemetryRecorderPluginManager):
        """
        Initialize the coordinator with a recorder manager.

        Parameters
        ----------
        recorder_plugin_manager : TelemetryRecorderPluginManager
            Manager responsible for registering and loading telemetry recorders.
        """
        self.recorder_plugin_manager = (
            recorder_plugin_manager or TelemetryRecorderPluginManager()
        )

    def initialize(self) -> None:
        """
        Register lifecycle hooks into Locust events.

        Steps
        -----
        1. Register worker metadata handlers.
        2. Load registered recorders on Locust init.
        3. Setup metadata propagation at test start.
        4. Cleanup metadata at test stop (future extension).

        Notes
        -----
        - Safe to call multiple times; only registers hooks once.
        """
        if self._initialized:
            return

        events.init_command_line_parser.add_listener(self._add_cli_arguments)
        events.init.add_listener(self._configure_logging)
        events.init.add_listener(self._register_metadata_handler)
        events.init.add_listener(self.recorder_plugin_manager.load_recorder_plugins)
        events.test_start.add_listener(self._setup_metadata)

        self._initialized = True

        logger.debug("[TelemetryCoordinator] Initialized and hooks registered")

    def _add_cli_arguments(self, parser: LocustArgumentParser):
        """
        Register all the cli from different recorders

        This allows each telemetry recorder to configure its own clis

        Parameters
        ----------
        parser : LocustArgumentParser
            The Locust LocustArgumentParser instance.
        """
        group = register_telemetry_cli_args(parser)
        for p in self.recorder_plugin_manager.recorder_plugins:
            p.add_cli_arguments(group)

    def _configure_logging(self, *args, **kwargs):
        """Register the logging configuration"""
        configure_logging()

    def _register_metadata_handler(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Register worker-side message handler for test metadata.

        This allows the master process to send metadata (e.g., testplan,
        run ID) to workers during test startup.

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        **kwargs : Any
            Additional event system arguments (unused).
        """
        if isinstance(environment.runner, WorkerRunner):
            environment.runner.register_message(
                "set_metadata",
                lambda msg, **kw: apply_worker_metadata(environment, msg.data),
            )
            logger.info("[Worker] Metadata handler registered successfully")

    def _setup_metadata(self, environment: Environment, **kwargs: Any) -> None:
        """
        Setup and propagate test metadata from master to workers.

        On test start, the master gathers metadata (e.g., testplan name,
        run ID) and sends it to all workers.

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        **kwargs : Any
            Additional event system arguments (unused).
        """
        if isinstance(environment.runner, MasterRunner):
            set_test_metadata(environment)
            metadata = get_test_metadata(environment)
            logger.info(
                "Sending test metadata to workers", extra={"metadata": metadata}
            )
            environment.runner.send_message("set_metadata", metadata)
