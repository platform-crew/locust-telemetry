from locust.runners import MasterRunner

from locust_telemetry.core_telemetry.constants import LocustTestEvent
from locust_telemetry.core_telemetry.mixins import LocustTelemetryCommonRecorderMixin


class DummyRecorder(LocustTelemetryCommonRecorderMixin):
    """A dummy class to test the telemetry mixin."""

    def __init__(self, env):
        self.env = env
        self.logged = []

    def log_telemetry(self, **kwargs):
        """Capture telemetry logs for assertions."""
        self.logged.append(kwargs)


def test_on_usage_monitor_logs_telemetry(mock_env):
    """
    Test that on_usage_monitor logs CPU and memory usage correctly.

    Memory usage should be converted from bytes to MiB.
    """
    mock_env.runner.__class__ = MasterRunner
    recorder = DummyRecorder(env=mock_env)
    cpu_usage = 55.5
    memory_bytes = 50 * 1024 * 1024  # 50 MiB in bytes

    recorder.on_usage_monitor(mock_env, cpu_usage=cpu_usage, memory_usage=memory_bytes)

    log = recorder.logged[0]
    assert log["telemetry"] == LocustTestEvent.USAGE.value
    assert log["cpu_usage"] == cpu_usage
    # Memory should be in MiB
    assert log["memory_usage"] == memory_bytes / 1024 / 1024
    assert log["source_type"] == "MasterRunner"


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
    expected_text = (
        f"{mock_env.parsed_options.testplan} high CPU usage " f"({cpu_usage:.2f}%)"
    )
    assert log["text"] == expected_text


def test_on_test_start_adds_listeners(mock_env):
    """
    Test that on_test_start attaches CPU and usage_monitor listeners to the environment.
    """
    recorder = DummyRecorder(env=mock_env)
    recorder.on_test_start()

    mock_env.events.cpu_warning.add_listener.assert_called_once_with(
        recorder.on_cpu_warning
    )
    mock_env.events.usage_monitor.add_listener.assert_called_once_with(
        recorder.on_usage_monitor
    )


def test_on_test_stop_removes_listeners(mock_env):
    """
    Test that on_test_stop removes CPU and usage_monitor listeners from the environment.
    """
    recorder = DummyRecorder(env=mock_env)
    recorder.on_test_stop()

    mock_env.events.cpu_warning.remove_listener.assert_called_once_with(
        recorder.on_cpu_warning
    )
    mock_env.events.usage_monitor.remove_listener.assert_called_once_with(
        recorder.on_usage_monitor
    )
