import logging
from typing import Any

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from locust_telemetry import config

logger = logging.getLogger(__name__)


def configure_otel(environment: Any) -> Any:
    """
    Configure and initialize OpenTelemetry metrics for a Locust environment.

    This function sets up an OTLP exporter with a periodic metrics reader,
    attaches it to a MeterProvider, and registers it as the global meter provider.

    Parameters
    ----------
    environment : Any
        Locust environment object containing parsed options for OTEL configuration.
        Expected attributes:
            - lt_otel_exporter_otlp_endpoint : str
            - lt_otel_exporter_otlp_insecure : bool
            - lt_stats_recorder_interval : int (seconds)
    """
    # Create the OTLP exporter gRPC
    exporter = OTLPMetricExporter(
        endpoint=environment.parsed_options.lt_otel_exporter_otlp_endpoint,  # gRPC
        insecure=environment.parsed_options.lt_otel_exporter_otlp_insecure,
    )

    # Create a periodic exporting metric reader
    reader = PeriodicExportingMetricReader(
        exporter,
        export_interval_millis=(
            environment.parsed_options.lt_stats_recorder_interval * 1000
        ),
    )

    # Set up the meter provider with the reader
    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)
    environment.otel_meter = metrics.get_meter(config.TELEMETRY_OTEL_METRICS_METER)
    environment.otel_provider = provider
    return environment.otel_meter
