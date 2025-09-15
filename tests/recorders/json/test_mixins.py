from unittest.mock import MagicMock, patch

import gevent
from locust.runners import MasterRunner

from locust_telemetry.recorders.json.constants import LocustTestEvent
from locust_telemetry.recorders.json.mixins import (
    LocustJsonTelemetryCommonRecorderMixin,
)


class DummyRecorder(LocustJsonTelemetryCommonRecorderMixin):
    """A dummy class to test the telemetry mixin."""

    def __init__(self, env):
        self.env = env
        self.logged = []

    def log_telemetry(self, **kwargs):
        """Capture telemetry logs for assertions."""
        self.logged.append(kwargs)


def test_log_usage_monitor_telemetry(mock_env):
    """
    Test that on_usage_monitor logs CPU and memory usage correctly.

    Memory usage should be converted from bytes to MiB.
    """
    mock_env.runner.__class__ = MasterRunner
    recorder = DummyRecorder(env=mock_env)

    # Patch psutil.Process().cpu_percent and memory_info
    with patch(
        "locust_telemetry.recorders.json.mixins."
        "LocustJsonTelemetryCommonRecorderMixin._process"
    ) as mock_process:
        mock_process.cpu_percent = MagicMock(return_value=50.0)
        mock_process.memory_info = MagicMock(
            return_value=MagicMock(rss=1024 * 1024 * 100)
        )

        # Patch gevent.sleep to break after first iteration
        with patch("gevent.sleep", side_effect=gevent.GreenletExit):
            # Should not raise error
            recorder._start_recording_system_metrics()

    # Validate that log_telemetry was called at least once
    assert len(recorder.logged) > 0
    log_entry = recorder.logged[0]
    assert log_entry["telemetry"] == LocustTestEvent.USAGE.value
    assert log_entry["cpu_usage"] == 50.0
    assert log_entry["memory_usage"] == 100  # in MiB


def test_on_cpu_warning_logs_telemetry(mock_env):
    """
    Test that on_cpu_warning logs CPU warning correctly.

    It should include the testplan name in the text and optional message.
    """
    recorder = DummyRecorder(env=mock_env)
    cpu_usage = 90.0
    message = "High CPU"

    recorder.on_cpu_warning(mock_env, cpu_usage=cpu_usage, message=message)

    log = recorder.logged[0]
    assert log["telemetry"] == LocustTestEvent.CPU_WARNING.value
    assert log["cpu_usage"] == cpu_usage
    assert log["message"] == message


def test_on_test_start_adds_listeners(mock_env):
    """
    Test that on_test_start attaches CPU and usage_monitor listeners to the environment.
    """
    recorder = DummyRecorder(env=mock_env)
    recorder.on_test_start()

    # Assert CPU warning listener added
    mock_env.events.cpu_warning.add_listener.assert_called_once_with(
        recorder.on_cpu_warning
    )

    # Patch gevent.spawn to return a mock greenlet
    mock_greenlet = MagicMock()
    with patch("gevent.spawn", return_value=mock_greenlet) as mock_spawn:
        recorder.on_test_start()

        # Assert gevent.spawn called with log_usage_monitor
        mock_spawn.assert_called_once_with(recorder._start_recording_system_metrics)

        # Assert the greenlet is stored in _usage_monitor_logger
        assert recorder._system_metrics_logger == mock_greenlet


def test_on_test_stop_removes_listeners_and_kills_logger(mock_env):
    """
    On test stop make sure, events listeners are removed and gevent process are killed
    """
    recorder = DummyRecorder(env=mock_env)
    # Mock a running gevent Greenlet
    mock_greenlet = MagicMock()
    recorder._system_metrics_logger = mock_greenlet

    # Call the method
    recorder.on_test_stop()

    # Assert CPU warning listener removed
    mock_env.events.cpu_warning.remove_listener.assert_called_once_with(
        recorder.on_cpu_warning
    )

    # Assert greenlet is killed and attribute cleared
    mock_greenlet.kill.assert_called_once()
    assert recorder._system_metrics_logger is None


def test_on_test_stop_without_logger():
    """
    On test stop if there are gvent process, make sure test_
    stop doesn't raise any error
    """
    # Setup mock environment
    mock_env = MagicMock()
    recorder = DummyRecorder(env=mock_env)
    recorder._usage_monitor_logger = None  # no logger running

    # Call the method
    recorder.on_test_stop()

    # CPU listener should still be removed
    mock_env.events.cpu_warning.remove_listener.assert_called_once_with(
        recorder.on_cpu_warning
    )

    # No greenlet, attribute should remain None
    assert recorder._usage_monitor_logger is None
