import logging

from locust.env import Environment

from locust_telemetry.core.recorder import (
    MasterTelemetryRecorder,
    WorkerTelemetryRecorder,
)
from locust_telemetry.recorders.json.handlers import (
    JsonTelemetryLifecycleHandler,
    JsonTelemetryOutputHandler,
    JsonTelemetryRequestHandler,
    JsonTelemetrySystemMetricsHandler,
)

logger = logging.getLogger(__name__)


class MasterLocustJsonTelemetryRecorder(MasterTelemetryRecorder):

    def __init__(self, env: Environment):
        super().__init__(
            env,
            output_handler_cls=JsonTelemetryOutputHandler,
            lifecycle_handler_cls=JsonTelemetryLifecycleHandler,
            system_handler_cls=JsonTelemetrySystemMetricsHandler,
            requests_handler_cls=JsonTelemetryRequestHandler,
        )


class WorkerLocustJsonTelemetryRecorder(WorkerTelemetryRecorder):

    def __init__(self, env: Environment):
        super().__init__(
            env,
            output_handler_cls=JsonTelemetryOutputHandler,
            lifecycle_handler_cls=JsonTelemetryLifecycleHandler,
            system_handler_cls=JsonTelemetrySystemMetricsHandler,
            requests_handler_cls=JsonTelemetryRequestHandler,
        )
