import logging
from unittest.mock import patch

from locust.env import Environment

from locust_telemetry.common.telemetry import TelemetryData
from locust_telemetry.core.recorder import BaseTelemetryRecorder


def test_recorder_initialization(
    recorder: BaseTelemetryRecorder, mock_env: Environment
) -> None:
    """Ensure the recorder is initialized with the given environment."""
    assert recorder.env is mock_env
    assert recorder.name == "base"


def test_log_telemetry_calls_logger_info(recorder: BaseTelemetryRecorder) -> None:
    """Verify that log_telemetry calls logger.info with correct payload."""
    telemetry = TelemetryData(type="event", name="dummy_event")

    with patch.object(
        logging.getLogger("locust_telemetry.core.recorder"), "info"
    ) as mock_info:
        recorder.log_telemetry(telemetry, custom_key="custom_value")
        mock_info.assert_called_once()
        log_args, log_kwargs = mock_info.call_args
        # First arg is the message string
        assert log_args[0] == f"Recording telemetry: {telemetry.name}"
        # Extra contains telemetry dictionary
        extra = log_kwargs.get("extra", {}).get("telemetry", {})
        assert extra.get("run_id") == recorder.env.run_id
        assert extra.get("testplan") == recorder.env.parsed_options.testplan
        # Custom keyword args are included
        assert extra.get("custom_key") == "custom_value"
