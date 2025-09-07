from locust.argument_parser import LocustArgumentParser
from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry.core.plugin import BaseTelemetryPlugin


def test_add_arguments_default_noop(dummy_plugin: BaseTelemetryPlugin):
    """Verify that the default add_arguments does nothing (no error raised)."""
    parser = LocustArgumentParser()
    # This should not raise an exception
    dummy_plugin.add_arguments(parser)


def test_register_master_telemetry_recorder_called_on_master_load(
    mock_env: Environment, dummy_plugin: BaseTelemetryPlugin
):
    """Ensure load() calls master recorder when runner is MasterRunner."""
    mock_env.runner.__class__ = MasterRunner
    dummy_plugin.load(mock_env)
    assert getattr(dummy_plugin, "master_loaded", False)
    assert not getattr(dummy_plugin, "worker_loaded", False)


def test_register_worker_telemetry_recorder_called_on_worker_load(
    mock_env: Environment, dummy_plugin: BaseTelemetryPlugin
):
    """Ensure load() calls worker recorder when runner is WorkerRunner."""
    mock_env.runner.__class__ = WorkerRunner
    dummy_plugin.load(mock_env)
    assert getattr(dummy_plugin, "worker_loaded", False)
    assert not getattr(dummy_plugin, "master_loaded", False)


def test_load_calls_correct_recorder_multiple_times(
    mock_env: Environment, dummy_plugin: BaseTelemetryPlugin
):
    """Verify load dispatches correctly depending on runner type."""
    # Master
    mock_env.runner.__class__ = MasterRunner
    dummy_plugin.master_loaded = False
    dummy_plugin.worker_loaded = False
    dummy_plugin.load(mock_env)
    assert dummy_plugin.master_loaded
    assert not dummy_plugin.worker_loaded

    # Worker
    mock_env.runner.__class__ = WorkerRunner
    dummy_plugin.master_loaded = False
    dummy_plugin.worker_loaded = False
    dummy_plugin.load(mock_env)
    assert dummy_plugin.worker_loaded
    assert not dummy_plugin.master_loaded
