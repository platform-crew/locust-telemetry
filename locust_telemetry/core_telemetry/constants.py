from locust_telemetry.common.telemetry import BaseTelemetryEnum, TelemetryData


class LocustTestEvent(BaseTelemetryEnum):
    """Events emitted during the test lifecycle."""

    START = TelemetryData("event", "event.test.start")
    STOP = TelemetryData("event", "event.test.stop")
    SPAWN_COMPLETE = TelemetryData("event", "event.spawn.complete")
    CPU_WARNING = TelemetryData("event", "event.cpu.warning")


class RequestMetric(BaseTelemetryEnum):
    """Metrics collected for HTTP requests and endpoints."""

    CURRENT_STATS = TelemetryData("metric", "metric.request.current.stats")
    FINAL_STATS = TelemetryData("metric", "metric.request.final.stats")
    ENDPOINT_STATS = TelemetryData("metric", "metric.request.endpoint.stats")
    ENDPOINT_ERRORS = TelemetryData("metric", "metric.request.endpoint.errors")
