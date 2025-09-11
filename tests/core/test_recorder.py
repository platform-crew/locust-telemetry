from unittest.mock import patch

from locust_telemetry.common.telemetry import TelemetryData
from locust_telemetry.core.recorder import TelemetryBaseRecorder


def test_initialization_sets_env_and_metadata(recorder, mock_env):
    """
    Ensure TelemetryRecorderBase initializes environment, username, hostname, and pid.
    """
    assert recorder.env is mock_env
    assert hasattr(recorder, "_username")
    assert hasattr(recorder, "_hostname")
    assert hasattr(recorder, "_pid")


def test_log_telemetry_calls_logger_info(recorder, mock_env):
    """
    Verify log_telemetry calls logger.info with expected structure.
    """
    telemetry = TelemetryData(name="event1", type="metric")
    extra_kwargs = {"custom_field": 42}

    with patch("locust_telemetry.core.recorder.logger.info") as mock_info:
        recorder.log_telemetry(telemetry, **extra_kwargs)

    # Check logger.info was called
    mock_info.assert_called_once()
    args, kwargs = mock_info.call_args

    # First argument is the log message
    assert args[0] == f"Recording telemetry: {telemetry.name}"

    # 'extra' contains structured telemetry
    extra = kwargs.get("extra", {})
    telemetry_dict = extra.get("telemetry", {})
    assert telemetry_dict["run_id"] == mock_env.run_id
    assert telemetry_dict["testplan"] == mock_env.parsed_options.testplan
    assert telemetry_dict["telemetry_name"] == telemetry.name
    assert telemetry_dict["telemetry_type"] == telemetry.type
    assert telemetry_dict["recorder"] == recorder.name
    # Custom kwargs should be merged
    assert telemetry_dict["custom_field"] == 42


def test_default_name_classvar():
    """Ensure the default recorder name is 'base'."""
    assert TelemetryBaseRecorder.name == "base"
