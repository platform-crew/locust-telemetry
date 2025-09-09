"""
This module defines the base plugin interface for Locust Telemetry extensions.

Responsibilities
----------------
- Provide a consistent lifecycle for plugins across master and worker nodes.
- Allow plugins to define their own CLI arguments and environment variables.
- Automatically register master and worker recorders depending on runner type.
- Support multiple telemetry plugins within a single Locust session.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from locust.argument_parser import LocustArgumentParser
from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

logger = logging.getLogger(__name__)


# -------------------------------
# Base Telemetry Plugin Interface
# -------------------------------
class BaseTelemetryPlugin(ABC):
    """
    Abstract base class for Locust Telemetry plugins.

    Extend this class to implement custom telemetry features.

    Each plugin can:
    - Define optional CLI arguments for configuration
    - Register master-side recorders (for aggregating results/metrics)
    - Register worker-side recorders (for local data capture)
    """

    def add_arguments(self, parser: LocustArgumentParser) -> None:
        """
        Hook for registering plugin-specific CLI arguments or environment variables.

        Default: does nothing.
        Override in your plugin if runtime configuration is required.
        """
        pass

    @abstractmethod
    def load_master_telemetry_recorders(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Register recorders to run on the master process.

        Override this in your plugin to implement master-side behavior.
        """
        pass

    @abstractmethod
    def load_worker_telemetry_recorders(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Register recorders to run on each worker process.

        Override this in your plugin to implement worker-side behavior.
        """
        pass

    def load(self, environment: Environment, **kwargs: Any) -> None:
        """
        Entry point for plugin initialization.

        Automatically called by the plugin manager at test start.
        Dispatches to master or worker recorder registration depending
        on the current runner type.
        """
        if isinstance(environment.runner, MasterRunner):
            self.load_master_telemetry_recorders(environment, **kwargs)
        elif isinstance(environment.runner, WorkerRunner):
            self.load_worker_telemetry_recorders(environment, **kwargs)
