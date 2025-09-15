from unittest.mock import patch

import pytest
from locust.env import Environment

from locust_telemetry.recorders.json.locust.constants import LocustTestEvent
from locust_telemetry.recorders.json.locust.worker import (
    WorkerLocustJsonTelemetryRecorder,
)


@pytest.fixture
def recorder(mock_env: Environment) -> WorkerLocustJsonTelemetryRecorder:
    """Return a WorkerLocustJsonTelemetryRecorder instance for testing."""
    return WorkerLocustJsonTelemetryRecorder(env=mock_env)


def test_recorder_initialization_registers_event_listener(
    recorder: WorkerLocustJsonTelemetryRecorder, mock_env: Environment
) -> None:
    """
    Ensure the recorder registers a listener for cpu_warning and system usage on init.
    """
    mock_env.events.test_start.add_listener.assert_called_once_with(
        recorder.on_test_start
    )
    mock_env.events.test_stop.add_listener.assert_called_once_with(
        recorder.on_test_stop
    )
    assert recorder.env is mock_env
    assert recorder.name == "worker_json_recorder"


def test_on_cpu_warning_calls_log_telemetry(
    recorder: WorkerLocustJsonTelemetryRecorder,
) -> None:
    """Ensure on_cpu_warning logs telemetry with correct payload."""
    cpu_usage = 85.5
    message = "High CPU"

    with patch.object(recorder, "log_telemetry") as mock_log:
        recorder.on_cpu_warning(recorder.env, cpu_usage=cpu_usage, message=message)
        mock_log.assert_called_once()
        call_args, call_kwargs = mock_log.call_args
        # Telemetry type is CPU_WARNING
        assert call_kwargs["telemetry"] == LocustTestEvent.CPU_WARNING.value
        # CPU usage is passed correctly
        assert call_kwargs["cpu_usage"] == cpu_usage
        # Message is passed correctly
        assert call_kwargs["message"] == message
        # Text contains testplan and CPU usage
        assert recorder.env.parsed_options.testplan in call_kwargs["text"]
        assert f"{cpu_usage:.2f}" in call_kwargs["text"]


def test_on_cpu_warning_with_default_message(
    recorder: WorkerLocustJsonTelemetryRecorder,
) -> None:
    """Ensure on_cpu_warning works if message is None."""
    cpu_usage = 92.3
    with patch.object(recorder, "log_telemetry") as mock_log:
        recorder.on_cpu_warning(recorder.env, cpu_usage=cpu_usage)
        mock_log.assert_called_once()
        call_kwargs = mock_log.call_args.kwargs
        # Message should be None
        assert call_kwargs["message"] is None
        # Telemetry type is still correct
        assert call_kwargs["telemetry"] == LocustTestEvent.CPU_WARNING.value
