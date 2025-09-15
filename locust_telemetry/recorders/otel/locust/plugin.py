import logging
from typing import Any, Dict

from locust.env import Environment

from locust_telemetry import config
from locust_telemetry.core.plugin import TelemetryRecorderPluginBase

logger = logging.getLogger(__name__)


class LocustOtelRecorderPlugin(TelemetryRecorderPluginBase):

    RECORDER_PLUGIN_ID = config.TELEMETRY_OTEL_RECORDER_PLUGIN_ID

    def add_test_metadata(self) -> Dict:
        return {}

    def add_cli_arguments(self, group: Any) -> None:
        pass

    def load_master_telemetry_recorders(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        pass

    def load_worker_telemetry_recorders(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        pass
