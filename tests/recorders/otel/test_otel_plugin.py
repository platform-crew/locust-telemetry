from unittest.mock import MagicMock, patch

from locust_telemetry import config
from locust_telemetry.recorders.otel.plugin import LocustOtelRecorderPlugin


def test_plugin_id_constant():
    """Plugin ID should match configured constant."""
    assert (
        LocustOtelRecorderPlugin.RECORDER_PLUGIN_ID
        == config.TELEMETRY_OTEL_RECORDER_PLUGIN_ID
    )


def test_add_test_metadata_returns_empty_dict():
    """add_test_metadata should return an empty dict."""
    plugin = LocustOtelRecorderPlugin()
    assert plugin.add_test_metadata() == {}


def test_add_cli_arguments_registers_all_options():
    """CLI arguments for OTEL should be registered."""
    plugin = LocustOtelRecorderPlugin()
    group = MagicMock()

    plugin.add_cli_arguments(group)

    assert group.add_argument.call_count == 2

    args = [call.args[0] for call in group.add_argument.call_args_list]
    assert "--lt-otel-exporter-otlp-endpoint" in args
    assert "--lt-otel-exporter-otlp-insecure" in args


@patch("locust_telemetry.recorders.otel.plugin.LocustOtelMasterNodeRecorder")
def test_load_master_recorders_creates_master_recorder(
    mock_master_recorder, mock_env_master
):
    """Master recorder should be initialized with correct handlers."""
    plugin = LocustOtelRecorderPlugin()

    plugin.load_master_recorders(mock_env_master)

    mock_master_recorder.assert_called_once()
    _, kwargs = mock_master_recorder.call_args

    assert kwargs["env"] is mock_env_master
    assert kwargs["output_handler_cls"].__name__ == "OtelOutputHandler"
    assert kwargs["lifecycle_handler_cls"].__name__ == "OtelLifecycleHandler"
    assert kwargs["system_handler_cls"].__name__ == "OtelSystemMetricsHandler"
    assert kwargs["requests_handler_cls"].__name__ == "OtelRequestHandler"


@patch("locust_telemetry.recorders.otel.plugin.LocustOtelWorkerNodeRecorder")
def test_load_worker_recorders_creates_worker_recorder(
    mock_worker_recorder, mock_env_worker
):
    """Worker recorder should be initialized with correct handlers."""
    plugin = LocustOtelRecorderPlugin()

    plugin.load_worker_recorders(mock_env_worker)

    mock_worker_recorder.assert_called_once()
    _, kwargs = mock_worker_recorder.call_args

    assert kwargs["env"] is mock_env_worker
    assert kwargs["output_handler_cls"].__name__ == "OtelOutputHandler"
    assert kwargs["lifecycle_handler_cls"].__name__ == "OtelLifecycleHandler"
    assert kwargs["system_handler_cls"].__name__ == "OtelSystemMetricsHandler"
    assert kwargs["requests_handler_cls"].__name__ == "OtelRequestHandler"


@patch("locust_telemetry.recorders.otel.plugin.configure_otel")
@patch("locust_telemetry.core.plugin.BaseRecorderPlugin.load")
def test_plugin_load_configures_otel_and_calls_super(
    mock_super_load,
    mock_configure_otel,
    mock_env,
):
    """load() should configure OTEL and call BaseRecorderPlugin.load."""
    plugin = LocustOtelRecorderPlugin()

    plugin.load(mock_env, foo="bar")

    mock_configure_otel.assert_called_once_with(mock_env)
    mock_super_load.assert_called_once_with(mock_env, foo="bar")
