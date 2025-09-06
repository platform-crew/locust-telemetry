from enum import Enum
from typing import NamedTuple


class MetricData(NamedTuple):
    type: str
    name: str


class EventsEnum(Enum):
    TEST_START_EVENT = MetricData("event", "event.test.start")
    TEST_STOP_EVENT = MetricData("event", "event.test.stop")
    SPAWN_COMPLETE_EVENT = MetricData("event", "event.spawn.complete")
    CPU_WARNING_EVENT = MetricData("event", "event.cpu.warning")


class MetricsEnum(Enum):
    REQUEST_CURRENT_STATS_METRIC = MetricData("metric", "metric.request.current.stats")
    REQUEST_FINAL_STATS_METRIC = MetricData("metric", "metric.request.final.stats")
    REQUEST_ENDPOINT_STATS_METRIC = MetricData(
        "metric", "metric.request.endpoint.stats"
    )
    REQUEST_ENDPOINT_ERRORS_METRIC = MetricData(
        "metric", "metric.request.endpoint.errors"
    )
