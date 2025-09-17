import logging

from locust.env import Environment

from locust_telemetry.core.recorder import (
    MasterTelemetryRecorder,
    WorkerTelemetryRecorder,
)
from locust_telemetry.recorders.otel.handlers import (
    OtelLifecycleHandler,
    OtelOutputHandler,
    OtelRequestHandler,
    OtelSystemMetricsHandler,
)

logger = logging.getLogger(__name__)


class MasterLocustOtelRecorder(MasterTelemetryRecorder):

    def __init__(self, env: Environment):
        super().__init__(
            env,
            output_handler_cls=OtelOutputHandler,
            lifecycle_handler_cls=OtelLifecycleHandler,
            system_handler_cls=OtelSystemMetricsHandler,
            requests_handler_cls=OtelRequestHandler,
        )


class WorkerLocustOtelRecorder(WorkerTelemetryRecorder):

    def __init__(self, env: Environment):
        super().__init__(
            env,
            output_handler_cls=OtelOutputHandler,
            lifecycle_handler_cls=OtelLifecycleHandler,
            system_handler_cls=OtelSystemMetricsHandler,
            requests_handler_cls=OtelRequestHandler,
        )
