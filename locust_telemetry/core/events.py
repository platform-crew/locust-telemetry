from enum import Enum


class TelemetryEventsEnum(Enum):

    # All test events
    TEST = "locust.tl.event.test.events"

    TEST_START = "locust.tl.event.test.start"
    TEST_STOP = "locust.tl.event.test.stop"
    SPAWNING_COMPLETE = "locust.tl.event.spawn.complete"
    CPU_WARNING = "locust.tl.event.cpu.warning"


class TelemetryMetricsEnum(Enum):

    CPU = "locust.tl.system.metric.cpu"
    MEMORY = "locust.tl.system.metric.mem"
    NETWORK = "locust.tl.system.metric.network"

    REQUEST_STATS = "locust.tl.request.metric.stats"
    REQUEST_SUCCESS = "locust.tl.request.metric.success"
    REQUEST_ERROR = "locust.tl.request.metric.error"

    USER = "locust.tl.user.metric.count"
