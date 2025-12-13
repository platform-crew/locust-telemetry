from unittest.mock import MagicMock, patch

from locust import events
from locust.argument_parser import LocustArgumentParser
from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry.core.coordinator import TelemetryCoordinator
from locust_telemetry.core.manager import RecorderPluginManager


def test_singleton_behavior():
    """Ensure TelemetryCoordinator enforces the singleton pattern."""
    mgr = RecorderPluginManager()
    coo1 = TelemetryCoordinator(mgr)
    coo2 = TelemetryCoordinator(mgr)
    assert coo1 is coo2


def test_initialize_registers_hooks(mock_env):
    """Verify that initialize registers all lifecycle hooks exactly once."""
    mgr = RecorderPluginManager()
    coo = TelemetryCoordinator(mgr)

    called_hooks = {"init_parser": [], "init": [], "test_start": []}

    # Patch Locust events to track listeners
    events.init_command_line_parser.add_listener = lambda f: called_hooks[
        "init_parser"
    ].append(f)
    events.init.add_listener = lambda f: called_hooks["init"].append(f)
    events.test_start.add_listener = lambda f: called_hooks["test_start"].append(f)

    coo.initialize()

    # Assert CLI, init, test_start hooks registered
    assert coo._initialized is True
    assert coo._add_cli_arguments in called_hooks["init_parser"]
    assert coo._configure_logging in called_hooks["init"]
    assert coo._register_metadata_handler in called_hooks["init"]
    assert coo.recorder_plugin_manager.load_recorder_plugins in called_hooks["init"]
    assert coo._setup_metadata in called_hooks["test_start"]

    # Calling initialize again should not add duplicate hooks
    coo.initialize()
    assert len(called_hooks["init_parser"]) == 1
    # 3 init listeners: logging + metadata + plugin
    assert len(called_hooks["init"]) == 3
    assert len(called_hooks["test_start"]) == 1


def test_configure_logging_calls_loggin_setup(mock_env):
    """Verify coordinator setups logging calls actual logging configuration func"""
    mgr = RecorderPluginManager()
    coo = TelemetryCoordinator(mgr)
    with patch(
        "locust_telemetry.core.coordinator.configure_logging"
    ) as mock_configure_logging:
        coo._configure_logging(mock_env)
        mock_configure_logging.assert_called_once()


def test_add_cli_arguments_calls_plugins():
    """Ensure _add_cli_arguments calls add_cli_arguments for each registered plugin."""
    mgr = RecorderPluginManager()
    mock_plugin = MagicMock()
    mock_plugin.add_cli_arguments = MagicMock()
    mgr.register_recorder_plugin(mock_plugin)
    coo = TelemetryCoordinator(mgr)

    parser = LocustArgumentParser()
    coo._add_cli_arguments(parser)
    mock_plugin.add_cli_arguments.assert_called_once()


def test_register_metadata_handler_registers_worker_handler(mock_env):
    """_register_metadata_handler registers a message handler for WorkerRunner."""
    mock_env.runner.__class__ = WorkerRunner
    coo = TelemetryCoordinator(MagicMock())
    coo._register_metadata_handler(mock_env)

    mock_env.runner.register_message.assert_called_once()
    args, _ = mock_env.runner.register_message.call_args
    assert args[0] == "set_metadata"
    assert callable(args[1])


def test_register_metadata_handler_skips_non_worker(mock_env):
    """_register_metadata_handler does nothing if runner is not WorkerRunner."""
    mock_env.runner.__class__ = MasterRunner
    coo = TelemetryCoordinator(MagicMock())
    coo._register_metadata_handler(mock_env)
    assert not mock_env.runner.register_message.called


def test_setup_metadata_for_master_sends_message(mock_env):
    """
    Verify on master node, coordinator initiates the metadata setup and
    sends message to worker
    """
    mgr = MagicMock(spec=RecorderPluginManager)
    mgr.register_plugin_metadata.return_value = {"foo": "bar"}

    coord = TelemetryCoordinator(mgr)
    mock_env.runner.__class__ = MasterRunner

    coord._setup_metadata(mock_env)

    mgr.register_plugin_metadata.assert_called_once_with(mock_env)
    mock_env.runner.send_message.assert_called_once_with("set_metadata", {"foo": "bar"})


def test_setup_metadata_does_nothing_for_worker(mock_env):
    """
    Verify on worker node, make sure coordinator doesn't initiates metadata
    collector and does not send any message.
    """
    mgr = MagicMock(spec=RecorderPluginManager)
    coord = TelemetryCoordinator(mgr)

    mock_env.runner.__class__ = WorkerRunner

    coord._setup_metadata(mock_env)

    mgr.register_plugin_metadata.assert_not_called()
    mock_env.runner.send_message.assert_not_called()
