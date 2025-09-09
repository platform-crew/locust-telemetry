"""
Tests for LocustTelemetryPlugin and entry_point.

These tests verify:
- CLI argument registration
- Master and worker recorder registration
- Proper dispatching via the plugin load method
- Plugin registration via entry_point
"""

from unittest.mock import patch

import pytest
from locust.argument_parser import LocustArgumentParser
from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry.core.manager import PluginManager
from locust_telemetry.core_telemetry.plugin import (
    LocustTelemetryPlugin,
    entry_point,
)


@pytest.fixture
def parser() -> LocustArgumentParser:
    """Provide a fresh Locust argument parser for testing."""
    return LocustArgumentParser()


def test_add_arguments_creates_parser_group(parser: LocustArgumentParser) -> None:
    """Verify that the plugin adds the correct CLI argument group and arguments."""
    plugin = LocustTelemetryPlugin()
    plugin.add_arguments(parser)

    # Ensure the group exists
    group = next(
        (
            g
            for g in parser._action_groups
            if "telemetry.locust - Locust Telemetry" in g.title
        ),
        None,
    )
    assert group is not None, "Telemetry argument group not found in parser"

    # Ensure the specific argument exists
    arg_names = [a.option_strings[0] for a in group._group_actions]
    assert "--locust-telemetry-recorder-interval" in arg_names


def test_register_master_telemetry_recorder_calls_master_recorder(
    mock_env: Environment,
) -> None:
    """Ensure the master recorder is instantiated during master registration."""
    plugin = LocustTelemetryPlugin()
    mock_env.runner.__class__ = MasterRunner

    with patch(
        "locust_telemetry.core_telemetry.plugin.MasterLocustTelemetryRecorder"
    ) as mock_recorder:
        plugin.load_master_telemetry_recorders(mock_env)
        mock_recorder.assert_called_once_with(env=mock_env)


def test_register_worker_telemetry_recorder_calls_worker_recorder(
    mock_env: Environment,
) -> None:
    """Ensure the worker recorder is instantiated during worker registration."""
    plugin = LocustTelemetryPlugin()
    mock_env.runner.__class__ = WorkerRunner

    with patch(
        "locust_telemetry.core_telemetry.plugin.WorkerLocustTelemetryRecorder"
    ) as mock_recorder:
        plugin.load_worker_telemetry_recorders(mock_env)
        mock_recorder.assert_called_once_with(env=mock_env)


def test_load_dispatches_to_master_recorder_when_master(mock_env: Environment) -> None:
    """Verify that load() dispatches to master recorder when runner is MasterRunner."""
    plugin = LocustTelemetryPlugin()
    mock_env.runner.__class__ = MasterRunner

    with patch.object(plugin, "load_master_telemetry_recorders") as mock_master:
        plugin.load(mock_env)
        mock_master.assert_called_once_with(mock_env)


def test_load_dispatches_to_worker_recorder_when_worker(mock_env: Environment) -> None:
    """Verify that load() dispatches to worker recorder when runner is WorkerRunner."""
    plugin = LocustTelemetryPlugin()
    mock_env.runner.__class__ = WorkerRunner

    with patch.object(plugin, "load_worker_telemetry_recorders") as mock_worker:
        plugin.load(mock_env)
        mock_worker.assert_called_once_with(mock_env)


def test_entry_point_registers_plugin_in_manager() -> None:
    """Ensure entry_point registers the LocustTelemetryPlugin in the manager."""
    manager = PluginManager()
    manager._plugins.clear()  # ensure clean state

    entry_point()
    assert any(isinstance(p, LocustTelemetryPlugin) for p in manager._plugins)
