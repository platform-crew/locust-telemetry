from unittest.mock import MagicMock, patch

from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry.core.manager import PluginManager, TelemetryManager
from locust_telemetry.core.plugin import BaseTelemetryPlugin


def test_singleton() -> None:
    """Ensure TelemetryManager implements a singleton pattern."""
    manager1 = TelemetryManager(plugin_manager=PluginManager())
    manager2 = TelemetryManager(plugin_manager=PluginManager())
    assert manager1 is manager2
    assert manager1.plugin_manager is manager2.plugin_manager


def test_register_plugin(dummy_plugin) -> None:
    """Verify that plugins can be registered and are not duplicated."""
    plugin_manager = PluginManager()

    plugin_manager.register_plugin(dummy_plugin)
    assert dummy_plugin in plugin_manager._plugins

    # Re-registering should not duplicate
    plugin_manager.register_plugin(dummy_plugin)
    assert plugin_manager._plugins.count(dummy_plugin) == 1


def test_load_plugins_calls_plugin_load(mock_env) -> None:
    """Ensure load_plugins calls each plugin's load method."""
    plugin_manager = PluginManager()
    dummy_plugin = MagicMock(spec=BaseTelemetryPlugin)

    plugin_manager.register_plugin(dummy_plugin)
    plugin_manager.load_plugins(mock_env)

    dummy_plugin.load.assert_called_once_with(environment=mock_env)


def test_add_arguments() -> None:
    """Ensure TelemetryManager adds CLI arguments."""
    manager = TelemetryManager(plugin_manager=PluginManager())
    parser = MagicMock()
    manager._add_arguments(parser)
    parser.add_argument_group.assert_called_once()


def test_setup_logging_calls_configure_logging(mock_env) -> None:
    """Ensure configure_logging is called during _setup_logging."""
    manager = TelemetryManager(plugin_manager=PluginManager())

    with patch("locust_telemetry.core.manager.configure_logging") as mock_log:
        manager._setup_logging(mock_env)
        mock_log.assert_called_once()


def test_register_metadata_handler_for_worker(mock_env) -> None:
    """Ensure worker message handler is registered for WorkerRunner."""
    manager = TelemetryManager(plugin_manager=PluginManager())
    mock_env.runner.__class__ = WorkerRunner
    manager._register_metadata_handler(mock_env)

    mock_env.runner.register_message.assert_called_once()
    msg_type, func = mock_env.runner.register_message.call_args[0]
    assert msg_type == "set_metadata"
    assert callable(func)


def test_setup_metadata_for_master(mock_env) -> None:
    """Ensure master runner sets and sends metadata."""
    manager = TelemetryManager(plugin_manager=PluginManager())
    mock_env.runner.__class__ = MasterRunner

    with patch("locust_telemetry.core.manager.set_test_metadata") as mock_set, patch(
        "locust_telemetry.core.manager.get_test_metadata",
        return_value={"run_id": "123"},
    ) as _:
        manager._setup_metadata(mock_env)
        mock_set.assert_called_once_with(mock_env)
        mock_env.runner.send_message.assert_called_once_with(
            "set_metadata", {"run_id": "123"}
        )


def test_remove_metadata_calls_unset() -> None:
    """Ensure _remove_metadata calls unset_test_metadata."""
    manager = TelemetryManager(plugin_manager=PluginManager())
    mock_env = MagicMock(spec=Environment)

    with patch("locust_telemetry.core.manager.unset_test_metadata") as mock_unset:
        manager._remove_metadata(mock_env)
        mock_unset.assert_called_once_with(mock_env)
