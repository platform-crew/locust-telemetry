from enum import Enum


class TelemetryEvent(Enum):

    TEST_START = "event.test.start"
    TEST_STOP = "event.test.stop"
    SPAWNING_COMPLETE = "event.spawn.complete"
    CPU_WARNING = "event.cpu.warning"


class TelemetryMetric(Enum):

    CPU_USAGE = "metric.system.cpu"
    MEMORY_USAGE = "metric.system.mem"
    CURRENT_REQUEST_STATS = "metric.requests.stats.current"
    REQUEST_DURATION = "metric.requests.stats.duration"
    FINAL_REQUEST_STATS = "metric.requests.stats.final"
    FINAL_REQUEST_SUCCESS_STATS = "metric.requests.stats.final.success"
    FINAL_REQUEST_ERROR_STATS = "metric.requests.stats.final.errors"
