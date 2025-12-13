from unittest.mock import MagicMock, patch

from locust_telemetry.recorders.json.plugin import LocustJsonRecorderPlugin


def test_add_test_metadata_returns_empty_dict():
    """add_test_metadata should return an empty dictionary."""
    plugin = LocustJsonRecorderPlugin()
    metadata = plugin.add_test_metadata()
    assert metadata == {}


def test_add_cli_arguments_does_nothing():
    """add_cli_arguments is a no-op and should not raise exceptions."""
    plugin = LocustJsonRecorderPlugin()
    mock_group = MagicMock()
    plugin.add_cli_arguments(mock_group)


@patch("locust_telemetry.recorders.json.plugin.LocustJsonMasterNodeRecorder")
def test_load_master_recorders_calls_recorder(mock_recorder_cls, mock_env):
    """
    load_master_recorders should instantiate the master node recorder with
    correct handlers.
    """
    plugin = LocustJsonRecorderPlugin()
    plugin.load_master_recorders(mock_env)

    mock_recorder_cls.assert_called_once()
    args, kwargs = mock_recorder_cls.call_args
    assert kwargs["env"] == mock_env
    assert kwargs["output_handler_cls"].__name__ == "JsonTelemetryOutputHandler"
    assert kwargs["lifecycle_handler_cls"].__name__ == "JsonTelemetryLifecycleHandler"
    assert kwargs["system_handler_cls"].__name__ == "JsonTelemetrySystemMetricsHandler"
    assert kwargs["requests_handler_cls"].__name__ == "JsonTelemetryRequestHandler"


@patch("locust_telemetry.recorders.json.plugin.LocustJsonWorkerNodeRecorder")
def test_load_worker_recorders_calls_recorder(mock_recorder_cls, mock_env):
    """
    load_worker_recorders should instantiate the worker node recorder with
    correct handlers.
    """
    plugin = LocustJsonRecorderPlugin()
    plugin.load_worker_recorders(mock_env)

    mock_recorder_cls.assert_called_once()
    args, kwargs = mock_recorder_cls.call_args
    assert kwargs["env"] == mock_env
    assert kwargs["output_handler_cls"].__name__ == "JsonTelemetryOutputHandler"
    assert kwargs["lifecycle_handler_cls"].__name__ == "JsonTelemetryLifecycleHandler"
    assert kwargs["system_handler_cls"].__name__ == "JsonTelemetrySystemMetricsHandler"
    assert kwargs["requests_handler_cls"].__name__ == "JsonTelemetryRequestHandler"
