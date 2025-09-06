"""
Tests for WorkerNodeStatsRecorder

These tests cover initialization, event handling, and metric logging
for the WorkerNodeStatsRecorder in Locust-Observability.
"""

import socket
from unittest.mock import patch

from locust_observability.metrics import EventsEnum
from locust_observability.recorders.system import WorkerNodeStatsRecorder


def test_worker_recorder_init_registers_listeners(mock_env):
    """
    Verify that initializing WorkerNodeStatsRecorder sets basic attributes
    and registers CPU warning event listener.
    """
    recorder = WorkerNodeStatsRecorder(mock_env)

    assert recorder._hostname == socket.gethostname()
    assert isinstance(recorder._pid, int)

    # Check that cpu_warning listener is registered
    assert mock_env.events.cpu_warning.add_listener.called
    args, kwargs = mock_env.events.cpu_warning.add_listener.call_args
    assert args[0] == recorder.on_cpu_warning


@patch.object(WorkerNodeStatsRecorder, "log_metrics")
def test_on_cpu_warning_logs_event(mock_log, mock_env):
    """
    Test that on_cpu_warning logs a CPU warning with correct metadata.
    """
    recorder = WorkerNodeStatsRecorder(mock_env)
    mock_env.parsed_options.testplan = "test-plan"

    recorder.on_cpu_warning(
        environment=mock_env, cpu_usage=87.5, message="High load", timestamp=1234567890
    )

    mock_log.assert_called_once_with(
        metric=EventsEnum.CPU_WARNING_EVENT.value,
        cpu_usage=87.5,
        message="High load",
        text="test-plan High CPU usage (87.50%)",
    )


@patch.object(WorkerNodeStatsRecorder, "log_metrics")
def test_on_cpu_warning_handles_optional_fields(mock_log, mock_env):
    """
    Test on_cpu_warning when optional fields (message, timestamp) are None.
    """
    recorder = WorkerNodeStatsRecorder(mock_env)
    mock_env.parsed_options.testplan = "test-plan"

    recorder.on_cpu_warning(environment=mock_env, cpu_usage=55.0)

    mock_log.assert_called_once_with(
        metric=EventsEnum.CPU_WARNING_EVENT.value,
        cpu_usage=55.0,
        message=None,
        text="test-plan High CPU usage (55.00%)",
    )
