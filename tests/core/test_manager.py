from unittest.mock import MagicMock, patch

from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry.core.manager import TelemetryPluginManager
from locust_telemetry.core.plugin import BaseTelemetryPlugin


def test_singleton(mock_env: Environment) -> None:
    """Ensure TelemetryPluginManager implements a singleton pattern."""
    manager1 = TelemetryPluginManager()
    manager2 = TelemetryPluginManager()
    assert manager1 is manager2


def test_register_plugin(
    mock_env: Environment, dummy_plugin: BaseTelemetryPlugin
) -> None:
    """Verify that plugins can be registered and are not duplicated."""
    manager = TelemetryPluginManager()
    manager.register_plugin(dummy_plugin)
    assert dummy_plugin in manager._plugins

    # Re-registering should not duplicate
    manager.register_plugin(dummy_plugin)
    assert manager._plugins.count(dummy_plugin) == 1


def test_on_init_command_line_parser_calls_plugin_add_arguments(
    mock_env: Environment, dummy_plugin: BaseTelemetryPlugin
) -> None:
    """Ensure that plugin CLI argument hooks are called during init."""
    manager = TelemetryPluginManager()
    manager.register_plugin(dummy_plugin)

    parser = MagicMock()
    manager._on_init_command_line_parser(parser)
    assert dummy_plugin.added_args


def test_on_init_calls_configure_logging(mock_env: Environment) -> None:
    """Ensure configure_logging is called during manager initialization."""
    manager = TelemetryPluginManager()
    with patch("locust_telemetry.core.manager.configure_logging") as mock_log:
        manager._on_init(mock_env)
        mock_log.assert_called_once()


def test_on_init_worker_registers_message_handler(mock_env: Environment) -> None:
    """Ensure worker initialization registers metadata message handler."""
    manager = TelemetryPluginManager()
    mock_env.runner.__class__ = WorkerRunner
    manager._on_init_worker(mock_env)

    mock_env.runner.register_message.assert_called_once()
    args, _ = mock_env.runner.register_message.call_args
    msg_type, func = args
    assert msg_type == "set_metadata"
    assert callable(func)


def test_on_test_start_master_sets_metadata(mock_env: Environment) -> None:
    """Ensure master initialization sets test metadata."""
    manager = TelemetryPluginManager()
    mock_env.runner.__class__ = MasterRunner
    with patch("locust_telemetry.core.manager.set_test_metadata") as mock_set:
        manager._on_test_start(mock_env)
        mock_set.assert_called_once_with(mock_env)


def test_on_test_start_loads_plugins_on_master(
    mock_env: Environment, dummy_plugin: BaseTelemetryPlugin
) -> None:
    """Ensure plugins are loaded on master runner during test start."""
    manager = TelemetryPluginManager()
    manager.register_plugin(dummy_plugin)

    mock_env.runner.__class__ = MasterRunner
    with patch(
        "locust_telemetry.core.manager.get_test_metadata",
        return_value={"run_id": "123"},
    ):
        manager._on_test_start(mock_env)

    assert dummy_plugin.master_loaded


def test_on_test_start_loads_plugins_on_worker(
    mock_env: Environment, dummy_plugin: BaseTelemetryPlugin
) -> None:
    """Ensure plugins are loaded on worker runner during test start."""
    manager = TelemetryPluginManager()
    manager.register_plugin(dummy_plugin)

    mock_env.runner.__class__ = WorkerRunner
    manager._on_test_start(mock_env)

    assert dummy_plugin.worker_loaded
