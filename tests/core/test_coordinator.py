"""
Tests for TelemetryCoordinator with updated CLI hook handling.
"""

from unittest.mock import MagicMock, patch

import pytest
from locust import events
from locust.argument_parser import LocustArgumentParser
from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry.core.coordinator import TelemetryCoordinator
from locust_telemetry.core.manager import TelemetryRecorderPluginManager


@pytest.fixture
def mock_env():
    """Return a mocked Locust Environment with runner."""
    env = MagicMock()
    env.runner = MagicMock()
    env.parsed_options = MagicMock()
    env.parsed_options.testplan = "test-plan"
    return env


def test_singleton_behavior():
    """Ensure TelemetryCoordinator enforces the singleton pattern."""
    mgr = TelemetryRecorderPluginManager()
    coo1 = TelemetryCoordinator(mgr)
    coo2 = TelemetryCoordinator(mgr)
    assert coo1 is coo2


def test_initialize_registers_hooks(mock_env):
    """Verify that initialize registers all lifecycle hooks exactly once."""
    mgr = TelemetryRecorderPluginManager()
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
    assert coo._register_metadata_handler in called_hooks["init"]
    assert coo.recorder_plugin_manager.load_recorder_plugins in called_hooks["init"]
    assert coo._setup_metadata in called_hooks["test_start"]

    # Calling initialize again should not add duplicate hooks
    coo.initialize()
    assert len(called_hooks["init_parser"]) == 1
    # 3 init listeners: logging + metadata + plugin
    assert len(called_hooks["init"]) == 3
    assert len(called_hooks["test_start"]) == 1


def test_add_cli_arguments_calls_plugins():
    """Ensure _add_cli_arguments calls add_cli_arguments for each registered plugin."""
    mgr = TelemetryRecorderPluginManager()
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


def test_setup_metadata_sends_metadata_to_workers(mock_env):
    """_setup_metadata gathers metadata on MasterRunner and sends it to workers."""
    mock_env.runner.__class__ = MasterRunner
    coo = TelemetryCoordinator(MagicMock())

    # Patch metadata helpers
    with (
        patch("locust_telemetry.core.coordinator.set_test_metadata") as mock_set,
        patch(
            "locust_telemetry.core.coordinator.get_test_metadata",
            return_value={"run_id": "123"},
        ) as mock_get,
    ):
        coo._setup_metadata(mock_env)
        mock_set.assert_called_once_with(mock_env)
        mock_get.assert_called_once_with(mock_env)
        mock_env.runner.send_message.assert_called_once_with(
            "set_metadata", {"run_id": "123"}
        )


def test_setup_metadata_skips_non_master(mock_env):
    """_setup_metadata does nothing if runner is not MasterRunner."""
    mock_env.runner.__class__ = WorkerRunner
    coo = TelemetryCoordinator(MagicMock())
    coo._setup_metadata(mock_env)
    assert not mock_env.runner.send_message.called
