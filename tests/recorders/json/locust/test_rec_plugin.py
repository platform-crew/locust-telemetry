"""
Tests for LocustTelemetryPlugin.

These tests verify:
- Master/worker recorder registration
- Dispatching via plugin load()
- Plugin registration via @telemetry_plugin
"""

from unittest.mock import MagicMock, patch

from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry import config
from locust_telemetry.recorders.json.locust.master import (
    MasterLocustJsonTelemetryRecorder,
)
from locust_telemetry.recorders.json.locust.plugin import (
    LocustJsonTelemetryRecorderPlugin,
)
from locust_telemetry.recorders.json.locust.worker import (
    WorkerLocustJsonTelemetryRecorder,
)


def test_register_master_telemetry_recorder_calls_master_recorder(mock_env):
    """Ensure the master recorder is instantiated during master registration."""
    plugin = LocustJsonTelemetryRecorderPlugin()
    mock_env.runner.__class__ = MasterRunner

    with patch.object(
        MasterLocustJsonTelemetryRecorder, "__init__", return_value=None
    ) as mock_recorder:
        plugin.load_master_telemetry_recorders(mock_env)
        mock_recorder.assert_called_once_with(env=mock_env)


def test_register_worker_telemetry_recorder_calls_worker_recorder(mock_env):
    """Ensure the worker recorder is instantiated during worker registration."""
    plugin = LocustJsonTelemetryRecorderPlugin()
    mock_env.runner.__class__ = WorkerRunner

    with patch.object(
        WorkerLocustJsonTelemetryRecorder, "__init__", return_value=None
    ) as mock_recorder:
        plugin.load_worker_telemetry_recorders(mock_env)
        mock_recorder.assert_called_once_with(env=mock_env)


def test_load_dispatches_to_master_recorder_when_master(mock_env):
    """Verify that load() dispatches to master recorder when runner is MasterRunner."""
    plugin = LocustJsonTelemetryRecorderPlugin()
    mock_env.runner.__class__ = MasterRunner

    with patch.object(plugin, "load_master_telemetry_recorders") as mock_master:
        plugin.load(mock_env)
        mock_master.assert_called_once_with(mock_env)


def test_load_dispatches_to_worker_recorder_when_worker(mock_env):
    """Verify that load() dispatches to worker recorder when runner is WorkerRunner."""
    plugin = LocustJsonTelemetryRecorderPlugin()
    mock_env.runner.__class__ = WorkerRunner

    with patch.object(plugin, "load_worker_telemetry_recorders") as mock_worker:
        plugin.load(mock_env)
        mock_worker.assert_called_once_with(mock_env)


def test_add_cli_arguments_registers_expected_arguments():
    """
    Ensure that add_cli_arguments adds both stats and system usage interval arguments.
    """
    plugin = LocustJsonTelemetryRecorderPlugin()

    # Mock a parser group
    mock_group = MagicMock()
    mock_group.add_argument = MagicMock()

    plugin.add_cli_arguments(mock_group)

    # Capture the calls made to add_argument
    calls = mock_group.add_argument.call_args_list
    # first positional argument is the flag name
    added_args = [call[0][0] for call in calls]

    # Check that both arguments were added
    assert "--lt-stats-recorder-interval" in added_args
    assert "--lt-system-usage-recorder-interval" in added_args

    # Optional: check that default values are correct
    stats_call = next(
        call for call in calls if call[0][0] == "--lt-stats-recorder-interval"
    )
    assert stats_call[1]["default"] == config.DEFAULT_STATS_RECORDER_INTERVAL

    system_call = next(
        call for call in calls if call[0][0] == "--lt-system-usage-recorder-interval"
    )
    assert system_call[1]["default"] == config.DEFAULT_SYSTEM_USAGE_RECORDER_INTERVAL


def test_add_cli_arguments_sets_env_var_and_type():
    """
    Ensure that each CLI argument has correct type and env_var.
    """
    plugin = LocustJsonTelemetryRecorderPlugin()
    mock_group = MagicMock()
    plugin.add_cli_arguments(mock_group)

    calls = mock_group.add_argument.call_args_list

    stats_call = next(
        call for call in calls if call[0][0] == "--lt-stats-recorder-interval"
    )
    assert stats_call[1]["type"] is int
    assert stats_call[1]["env_var"] == "LOCUST_TELEMETRY_STATS_RECORDER_INTERVAL"

    system_call = next(
        call for call in calls if call[0][0] == "--lt-system-usage-recorder-interval"
    )
    assert system_call[1]["type"] is int
    assert (
        system_call[1]["env_var"] == "LOCUST_TELEMETRY_SYSTEM_USAGE_RECORDER_INTERVAL"
    )
