"""
Tests for LocustTelemetryPlugin.

These tests verify:
- Master/worker recorder registration
- Dispatching via plugin load()
- Plugin registration via @telemetry_plugin
"""

from unittest.mock import patch

from locust.runners import MasterRunner, WorkerRunner

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


def test_add_test_metadata():
    """
    Ensure calling a plugin's add_test_metadata return empty dict and
    follows the base signature.
    """
    plugin = LocustJsonTelemetryRecorderPlugin()
    metadata = plugin.add_test_metadata()
    assert isinstance(metadata, dict)
    assert metadata == {}
