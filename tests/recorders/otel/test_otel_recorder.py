from unittest.mock import MagicMock

from locust_telemetry.recorders.otel.recorder import (
    LocustOtelMasterNodeRecorder,
    LocustOtelWorkerNodeRecorder,
)


def test_master_recorder_initialization(mock_otel_env, otel_output_handler):
    """Master recorder should inherit from MasterNodeRecorder and store handlers."""
    recorder = LocustOtelMasterNodeRecorder(
        env=mock_otel_env,
        output_handler_cls=otel_output_handler.__class__,
        lifecycle_handler_cls=MagicMock(),
        system_handler_cls=MagicMock(),
        requests_handler_cls=MagicMock(),
    )

    # The env is stored correctly
    assert recorder.env is mock_otel_env

    # Handlers are assigned
    assert recorder.output.__class__ == otel_output_handler.__class__


def test_worker_recorder_initialization_adds_request_listener(mock_otel_env):
    """Worker recorder should attach on_request to env.events.request listener."""
    # Mock the request event list
    mock_requests_event = MagicMock()
    mock_otel_env.events.request = mock_requests_event

    # Patch handlers to pass to constructor
    output_cls = MagicMock()
    lifecycle_cls = MagicMock()
    system_cls = MagicMock()
    requests_cls = MagicMock()

    recorder = LocustOtelWorkerNodeRecorder(
        env=mock_otel_env,
        output_handler_cls=output_cls,
        lifecycle_handler_cls=lifecycle_cls,
        system_handler_cls=system_cls,
        requests_handler_cls=requests_cls,
    )

    # Ensure the event listener was added
    mock_requests_event.add_listener.assert_called_once_with(recorder.on_request)


def test_worker_on_request_delegates_to_requests_handler(mock_otel_env):
    """on_request() should forward call to requests handler's on_request."""
    requests_handler = MagicMock()
    recorder = LocustOtelWorkerNodeRecorder(
        env=mock_otel_env,
        output_handler_cls=MagicMock(),
        lifecycle_handler_cls=MagicMock(),
        system_handler_cls=MagicMock(),
        requests_handler_cls=lambda *args, **kwargs: requests_handler,
    )

    # Call on_request
    recorder.on_request(name="endpoint", response_time=123, exception=None)

    # Verify delegation
    requests_handler.on_request.assert_called_once_with(
        name="endpoint", response_time=123, exception=None
    )
