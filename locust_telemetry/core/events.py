from enum import Enum


class TelemetryEventsEnum(Enum):

    TEST = "locust.tl.locust.event.test"  # All test events

    TEST_START = "locust.tl.locust.event.test.start"
    TEST_STOP = "locust.tl.locust.event.test.stop"
    SPAWNING_COMPLETE = "locust.tl.locust.event.spawn.complete"
    CPU_WARNING = "locust.tl.locust.event.cpu.warning"


class TelemetryMetricsEnum(Enum):

    CPU = "locust.tl.system.metric.cpu"
    MEMORY = "locust.tl.system.metric.mem"
    NETWORK = "locust.tl.system.metric.network"

    REQUEST = "locust.tl.request.metric.stats"

    USER = "locust.tl.user.metric.stats"
