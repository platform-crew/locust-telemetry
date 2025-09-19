from enum import Enum


class TelemetryEventsEnum(Enum):

    TEST_START = "tl.locust.event.test.start"
    TEST_STOP = "tl.locust.event.test.stop"
    SPAWNING_COMPLETE = "tl.locust.event.spawn.complete"
    CPU_WARNING = "tl.locust.event.cpu.warning"


class TelemetryMetricsEnum(Enum):

    CPU = "tl.system.metric.cpu"
    MEMORY = "tl.system.metric.mem"
    NETWORK = "tl.system.metric.network"

    REQUEST = "tl.request.metric.stats"
