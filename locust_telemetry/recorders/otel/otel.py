import logging
from typing import Sequence

from locust.env import Environment
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

from locust_telemetry import config
from locust_telemetry.common import helpers as h
from locust_telemetry.core.events import TelemetryEventsEnum, TelemetryMetricsEnum
from locust_telemetry.recorders.otel.exceptions import OtelMetricAlreadyRegisteredError

logger = logging.getLogger(__name__)


class InstrumentRegistry:
    """
    Registry for managing OpenTelemetry metric instruments.

    This class provides a structured way to register and retrieve metric
    instruments, ensuring uniqueness and consistency across the application.
    """

    def __init__(self, meter: metrics.Meter):
        """
        Initialize the instrument registry.

        Parameters
        ----------
        meter : metrics.Meter
            The OpenTelemetry meter used to create instruments.
        """
        self._registry: dict[
            TelemetryEventsEnum | TelemetryMetricsEnum, h.InstrumentType
        ] = {}
        self.meter = meter

    def extend(self, items: Sequence[h.InstrumentSpec]) -> None:
        """
        Register multiple metric instruments in the registry.

        Parameters
        ----------
        items : Sequence[InstrumentSpec]
            A list of instrument specifications to register.

        Raises
        ------
        ValueError
            If a metric is already registered.
        """
        for spec in items:
            if spec.metric in self._registry:
                raise OtelMetricAlreadyRegisteredError(
                    f"[otel] Metric '{spec.metric.value}' already registered."
                )
            instrument = spec.factory(
                meter=self.meter,
                name=spec.metric.value,
                description=spec.metric.value,
                unit=spec.unit,
                callbacks=spec.callbacks or [],
            )
            self._registry[spec.metric] = instrument
            logger.debug(f"[otel] Registered metric: {spec.metric.value}")

    def get(
        self, key: TelemetryEventsEnum | TelemetryMetricsEnum
    ) -> h.InstrumentType | None:
        """
        Retrieve a registered instrument by its metric identifier.

        Parameters
        ----------
        key : TelemetryEventsEnum | TelemetryMetricsEnum
            The metric identifier.

        Returns
        -------
        h.InstrumentType
            The registered instrument, or None if not found.
        """
        return self._registry.get(key)


def configure_otel(environment: Environment) -> None:
    """
    Configure and initialize OpenTelemetry metrics for a Locust environment.

    This function:
    - Creates an OTLP exporter (gRPC).
    - Sets up a periodic metrics reader with the configured export interval.
    - Configures a MeterProvider with the given resource attributes.
    - Registers the meter provider globally.
    - Instantiates and attaches an InstrumentRegistry to the environment.

    Parameters
    ----------
    environment : Any
    Locust environment object containing parsed options for OTEL configuration.

    Returns
    -------
    Any
        The modified environment object with `otel_registry` attached.
    """

    # Define resource metadata for the service
    resource = Resource.create(
        {
            "service.name": config.TELEMETRY_SERVICE_NAME,
            "service.instance.id": h.get_source_id(environment),
        }
    )

    # Create the OTLP exporter (gRPC)
    exporter = OTLPMetricExporter(
        endpoint=environment.parsed_options.lt_otel_exporter_otlp_endpoint,
        insecure=environment.parsed_options.lt_otel_exporter_otlp_insecure,
        timeout=config.OTEL_EXPORTER_TIMEOUT,
    )

    # Create a periodic exporting metric reader
    reader = PeriodicExportingMetricReader(
        exporter,
        export_interval_millis=(
            environment.parsed_options.lt_stats_recorder_interval * 1000
        ),
    )

    # Set up the meter provider with the reader
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)

    # Attach an instrument registry to the environment
    environment.otel_registry = InstrumentRegistry(
        provider.get_meter(config.TELEMETRY_OTEL_METRICS_METER)
    )
    logger.info("[otel] OpenTelemetry metrics configured successfully")
