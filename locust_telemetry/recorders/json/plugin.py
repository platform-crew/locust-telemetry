"""
This module defines the `LocustJsonRecorderPlugin`, which integrates
telemetry recording into Locust runs. It initializes master and
worker telemetry recorders to capture lifecycle events, request
statistics, and worker system metrics.
"""

import logging
from typing import Any, Dict

from locust.env import Environment

from locust_telemetry import config
from locust_telemetry.core.plugin import BaseRecorderPlugin
from locust_telemetry.recorders.json.handlers import (
    JsonTelemetryLifecycleHandler,
    JsonTelemetryOutputHandler,
    JsonTelemetryRequestHandler,
    JsonTelemetrySystemMetricsHandler,
)
from locust_telemetry.recorders.json.recorder import (
    LocustJsonMasterNodeRecorder,
    LocustJsonWorkerNodeRecorder,
)

logger = logging.getLogger(__name__)


class LocustJsonRecorderPlugin(BaseRecorderPlugin):
    """
    Core telemetry recorder plugin for Locust.

    Responsibilities
    ----------------
    - Register CLI arguments for telemetry configuration.
    - Load master-side telemetry recorders.
    - Load worker-side telemetry recorders.
    """

    RECORDER_PLUGIN_ID = config.TELEMETRY_JSON_RECORDER_PLUGIN_ID

    def add_test_metadata(self) -> Dict:
        """
        This recorder plugin doesn't need any metadata other than the default
        available at config.DEFAULT_ENVIRONMENT_METADATA
        """
        return {}

    def add_cli_arguments(self, group: Any) -> None:
        """
        Register CLI arguments for this telemetry recorder plugin.

        Parameters
        ----------
        group : Any (_ArgumentGroup)
            The argument group to which telemetry recorder options are added.
        """
        pass

    def load_master_recorders(self, environment: Environment, **kwargs: Any) -> None:
        """
        Register the master-side telemetry recorder(s).

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        **kwargs : Any
            Additional context passed by the TelemetryCoordinator.
        """
        LocustJsonMasterNodeRecorder(
            env=environment,
            output_handler_cls=JsonTelemetryOutputHandler,
            lifecycle_handler_cls=JsonTelemetryLifecycleHandler,
            system_handler_cls=JsonTelemetrySystemMetricsHandler,
            requests_handler_cls=JsonTelemetryRequestHandler,
        )

    def load_worker_recorders(self, environment: Environment, **kwargs: Any) -> None:
        """
        Register the worker-side telemetry recorder(s).

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        **kwargs : Any
            Additional context passed by the TelemetryCoordinator.
        """
        LocustJsonWorkerNodeRecorder(
            env=environment,
            output_handler_cls=JsonTelemetryOutputHandler,
            lifecycle_handler_cls=JsonTelemetryLifecycleHandler,
            system_handler_cls=JsonTelemetrySystemMetricsHandler,
            requests_handler_cls=JsonTelemetryRequestHandler,
        )
