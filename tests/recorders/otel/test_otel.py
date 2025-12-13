from unittest.mock import MagicMock, patch

import pytest

from locust_telemetry import config
from locust_telemetry.common import helpers as h
from locust_telemetry.core.events import (
    TelemetryEventsEnum,
    TelemetryMetricsEnum,
)
from locust_telemetry.recorders.otel.exceptions import (
    OtelMetricAlreadyRegisteredError,
)
from locust_telemetry.recorders.otel.otel import (
    InstrumentRegistry,
    configure_otel,
)


def test_instrument_registry_registers_instruments():
    """InstrumentRegistry.extend should register instruments via factory."""
    meter = MagicMock()
    registry = InstrumentRegistry(meter=meter)

    instrument = MagicMock()
    factory = MagicMock(return_value=instrument)

    spec = h.InstrumentSpec(
        metric=TelemetryEventsEnum.TEST,
        unit="1",
        factory=factory,
    )

    registry.extend([spec])

    factory.assert_called_once_with(
        meter=meter,
        name=TelemetryEventsEnum.TEST.value,
        description=TelemetryEventsEnum.TEST.value,
        unit="1",
        callbacks=[],
    )
    assert registry.get(TelemetryEventsEnum.TEST) is instrument


def test_instrument_registry_duplicate_registration_raises():
    """Registering the same metric twice should raise."""
    meter = MagicMock()
    registry = InstrumentRegistry(meter=meter)

    spec = h.InstrumentSpec(
        metric=TelemetryMetricsEnum.CPU,
        unit="%",
        factory=MagicMock(),
    )

    registry.extend([spec])

    with pytest.raises(OtelMetricAlreadyRegisteredError):
        registry.extend([spec])


def test_instrument_registry_get_unknown_returns_none():
    """Unknown metric lookup should return None."""
    registry = InstrumentRegistry(meter=MagicMock())

    assert registry.get(TelemetryMetricsEnum.MEMORY) is None


@patch("locust_telemetry.recorders.otel.otel.metrics.set_meter_provider")
@patch("locust_telemetry.recorders.otel.otel.MeterProvider")
@patch("locust_telemetry.recorders.otel.otel.PeriodicExportingMetricReader")
@patch("locust_telemetry.recorders.otel.otel.OTLPMetricExporter")
@patch("locust_telemetry.recorders.otel.otel.Resource.create")
@patch("locust_telemetry.recorders.otel.otel.h.get_source_id")
def test_configure_otel_sets_registry_and_meter(
    mock_get_source_id,
    mock_resource_create,
    mock_exporter_cls,
    mock_reader_cls,
    mock_provider_cls,
    mock_set_provider,
    mock_env,
):
    """configure_otel should attach InstrumentRegistry and configure meter."""
    mock_get_source_id.return_value = "source-123"

    meter = MagicMock()
    provider = MagicMock()
    provider.get_meter.return_value = meter
    mock_provider_cls.return_value = provider

    configure_otel(mock_env)

    # Resource creation
    mock_resource_create.assert_called_once_with(
        {
            "service.name": config.TELEMETRY_SERVICE_NAME,
            "service.instance.id": "source-123",
        }
    )

    # Exporter created with env options
    mock_exporter_cls.assert_called_once_with(
        endpoint=mock_env.parsed_options.lt_otel_exporter_otlp_endpoint,
        insecure=mock_env.parsed_options.lt_otel_exporter_otlp_insecure,
        timeout=config.OTEL_EXPORTER_TIMEOUT,
    )

    # Reader created
    mock_reader_cls.assert_called_once()

    # Meter provider set globally
    mock_set_provider.assert_called_once_with(provider)

    # Registry attached
    assert hasattr(mock_env, "otel_registry")
    assert isinstance(mock_env.otel_registry, InstrumentRegistry)
    assert mock_env.otel_registry.meter is meter
