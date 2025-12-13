"""Base interface for Telemetry Recorder plugins in Locust."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry.core.exceptions import RecorderPluginError

logger = logging.getLogger(__name__)


class BaseRecorderPlugin(ABC):
    """
    Abstract base class for all telemetry recorder plugins.

    Extend this class to implement custom telemetry features such as
    metrics reporting, external integrations, or event capture.

    Each recorder plugin can:
    - Define optional CLI arguments for runtime configuration.
    - Register master-side recorders (for aggregation, central logging, etc.).
    - Register worker-side recorders (for local metric capture).
    """

    RECORDER_PLUGIN_ID: str | None = None

    @abstractmethod
    def add_test_metadata(self) -> Dict:
        """
        Add any metadata required by the plugin to both master and worker environment.
        Metadata that is returned from this method can be accessed from
        environment.telemetry_meta
        """

    @abstractmethod
    def add_cli_arguments(self, group: Any) -> None:
        """
        Register recorder plugin-specific CLI arguments or environment variables.

        Override in your plugin if runtime configuration is required.

        Parameters
        ----------
        group : _ArgumentGroup
            The argument parser group to which options can be added.
        """

    @abstractmethod
    def load_master_recorders(self, environment: Environment, **kwargs: Any) -> None:
        """
        Register telemetry recorders that should run on the master process.

        Override this method in your recorder plugin to implement master-side behavior.

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        **kwargs : Any
            Additional context passed by the coordinator or event system.
        """

    @abstractmethod
    def load_worker_recorders(self, environment: Environment, **kwargs: Any) -> None:
        """
        Register telemetry recorders that should run on each worker process.

        Override this method in your recorder plugin to implement worker-side behavior.

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        **kwargs : Any
            Additional context passed by the coordinator or event system.
        """

    def load(self, environment: Environment, **kwargs: Any) -> None:
        """
        Entry point for recorder plugin initialization.

        Automatically invoked by ``RecorderPluginManager`` during
        Locust's init phase. Dispatches to the correct recorder registration
        method depending on runner type.

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        **kwargs : Any
            Additional context passed by the coordinator or event system.
        """
        if self.RECORDER_PLUGIN_ID is None:
            raise RecorderPluginError(
                "Recorder plugin should have RECORDER_PLUGIN_ID attribute."
            )

        if isinstance(environment.runner, MasterRunner):
            self.load_master_recorders(environment, **kwargs)
        elif isinstance(environment.runner, WorkerRunner):
            self.load_worker_recorders(environment, **kwargs)
