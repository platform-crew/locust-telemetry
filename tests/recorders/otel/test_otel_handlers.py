from unittest.mock import MagicMock

import pytest
from opentelemetry.metrics import Observation

from locust_telemetry.core.events import TelemetryEventsEnum, TelemetryMetricsEnum
from locust_telemetry.recorders.otel.exceptions import OtelMetricNotRegisteredError
from locust_telemetry.recorders.otel.handlers import (
    OtelLifecycleHandler,
    OtelRequestHandler,
    OtelSystemMetricsHandler,
)


def test_output_handler_records_event(mock_otel_env, otel_output_handler):
    """record_event should increment TEST counter with attributes."""
    counter = MagicMock()
    mock_otel_env.otel_registry._registry[TelemetryEventsEnum.TEST] = counter

    otel_output_handler.record_event(TelemetryEventsEnum.TEST_START)

    counter.add.assert_called_once_with(
        1,
        attributes={
            "event": TelemetryEventsEnum.TEST_START.value,
            "ctx": "test",
        },
    )


def test_output_handler_event_metric_missing_raises(mock_otel_env, otel_output_handler):
    """record_event should raise if TEST metric not registered."""
    with pytest.raises(OtelMetricNotRegisteredError):
        otel_output_handler.record_event(TelemetryEventsEnum.TEST_START)


def test_output_handler_records_metric(mock_otel_env, otel_output_handler):
    """record_metrics should record value on registered instrument."""
    histogram = MagicMock()
    mock_otel_env.otel_registry._registry[TelemetryMetricsEnum.REQUEST_SUCCESS] = (
        histogram
    )

    otel_output_handler.record_metrics(
        TelemetryMetricsEnum.REQUEST_SUCCESS,
        123,
        endpoint="/test",
    )

    histogram.record.assert_called_once_with(
        123,
        attributes={
            "metric": TelemetryMetricsEnum.REQUEST_SUCCESS.value,
            "ctx": "test",
            "endpoint": "/test",
        },
    )


def test_lifecycle_handler_registers_instruments(mock_otel_env, otel_output_handler):
    """Lifecycle handler should register TEST and USER instruments."""
    OtelLifecycleHandler(otel_output_handler, mock_otel_env)

    assert TelemetryEventsEnum.TEST in mock_otel_env.otel_registry._registry
    assert TelemetryMetricsEnum.USER in mock_otel_env.otel_registry._registry


def test_user_count_callback(mock_otel_env, otel_output_handler):
    """User count callback should return Observation with runner user count."""
    handler = OtelLifecycleHandler(otel_output_handler, mock_otel_env)

    obs = handler._user_count_callback()

    assert isinstance(obs, list)
    assert isinstance(obs[0], Observation)
    assert obs[0].value == mock_otel_env.runner.user_count


def test_request_handler_success_records_success_metric(
    mock_otel_env, otel_output_handler
):
    """Successful request should record REQUEST_SUCCESS metric."""
    handler = OtelRequestHandler(otel_output_handler, mock_otel_env)

    success_hist = MagicMock()
    error_hist = MagicMock()

    mock_otel_env.otel_registry._registry[TelemetryMetricsEnum.REQUEST_SUCCESS] = (
        success_hist
    )
    mock_otel_env.otel_registry._registry[TelemetryMetricsEnum.REQUEST_ERROR] = (
        error_hist
    )

    handler.on_request(
        response_time=500,
        name="/fail",
        response=None,
        exception=Exception("boom"),
    )

    error_hist.record.assert_called_once_with(
        500,
        attributes={
            "metric": TelemetryMetricsEnum.REQUEST_ERROR.value,
            "ctx": "test",
            "endpoint": "/fail",
            "status_code": 500,
        },
    )
    success_hist.record.assert_not_called()


def test_request_handler_error_records_error_metric(mock_otel_env, otel_output_handler):
    """Errored request should record REQUEST_ERROR metric."""
    handler = OtelRequestHandler(otel_output_handler, mock_otel_env)
    success_hist = MagicMock()
    error_hist = MagicMock()

    mock_otel_env.otel_registry._registry[TelemetryMetricsEnum.REQUEST_SUCCESS] = (
        success_hist
    )
    mock_otel_env.otel_registry._registry[TelemetryMetricsEnum.REQUEST_ERROR] = (
        error_hist
    )

    handler.on_request(
        response_time=500,
        name="/fail",
        response=None,
        exception=Exception("boom"),
    )

    error_hist.record.assert_called_once()
    success_hist.record.assert_not_called()


def test_system_metrics_handler_registers_instruments(
    mock_otel_env, otel_output_handler
):
    """System metrics handler should register CPU, MEMORY, NETWORK."""
    OtelSystemMetricsHandler(otel_output_handler, mock_otel_env)
    assert TelemetryMetricsEnum.CPU in mock_otel_env.otel_registry._registry
    assert TelemetryMetricsEnum.MEMORY in mock_otel_env.otel_registry._registry
    assert TelemetryMetricsEnum.NETWORK in mock_otel_env.otel_registry._registry


def test_system_callbacks_return_observations(mock_otel_env, otel_output_handler):
    """System metric callbacks should return Observation objects."""
    handler = OtelSystemMetricsHandler(otel_output_handler, mock_otel_env)
    assert all(isinstance(o, Observation) for o in handler._cpu_usage_callback())
    assert all(isinstance(o, Observation) for o in handler._memory_usage_callback())
    assert all(isinstance(o, Observation) for o in handler._network_usage_callback())
