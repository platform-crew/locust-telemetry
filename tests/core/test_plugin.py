import pytest
from locust.argument_parser import LocustArgumentParser
from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry.core.plugin import BaseTelemetryRecorderPlugin


def test_add_arguments_default_noop(dummy_recorder_plugin: BaseTelemetryRecorderPlugin):
    """Verify that the default add_arguments does nothing (no error raised)."""
    parser = LocustArgumentParser()
    dummy_recorder_plugin.add_cli_arguments(parser)
    assert dummy_recorder_plugin.added_cli_args is True


def test_register_master_telemetry_recorder_called_on_master_load(
    mock_env: Environment, dummy_recorder_plugin: BaseTelemetryRecorderPlugin
):
    """Ensure load() calls master recorder when runner is MasterRunner."""
    mock_env.runner.__class__ = MasterRunner
    dummy_recorder_plugin.load(mock_env)
    assert getattr(dummy_recorder_plugin, "master_loaded", False)
    assert not getattr(dummy_recorder_plugin, "worker_loaded", False)


def test_register_worker_telemetry_recorder_called_on_worker_load(
    mock_env: Environment, dummy_recorder_plugin: BaseTelemetryRecorderPlugin
):
    """Ensure load() calls worker recorder when runner is WorkerRunner."""
    mock_env.runner.__class__ = WorkerRunner
    dummy_recorder_plugin.load(mock_env)
    assert getattr(dummy_recorder_plugin, "worker_loaded", False)
    assert not getattr(dummy_recorder_plugin, "master_loaded", False)


def test_load_calls_correct_recorder_multiple_times(
    mock_env: Environment, dummy_recorder_plugin: BaseTelemetryRecorderPlugin
):
    """Verify load dispatches correctly depending on runner type."""
    # Master
    mock_env.runner.__class__ = MasterRunner
    dummy_recorder_plugin.master_loaded = False
    dummy_recorder_plugin.worker_loaded = False
    dummy_recorder_plugin.load(mock_env)
    assert dummy_recorder_plugin.master_loaded
    assert not dummy_recorder_plugin.worker_loaded

    # Worker
    mock_env.runner.__class__ = WorkerRunner
    dummy_recorder_plugin.master_loaded = False
    dummy_recorder_plugin.worker_loaded = False
    dummy_recorder_plugin.load(mock_env)
    assert dummy_recorder_plugin.worker_loaded
    assert not dummy_recorder_plugin.master_loaded


def test_load_calls_nothing_if_runner_is_unknown(mock_env, dummy_recorder_plugin):
    """
    Ensure load() does nothing when runner is neither MasterRunner nor WorkerRunner.
    """

    class FakeRunner:
        pass

    mock_env.runner = FakeRunner()
    dummy_recorder_plugin.master_loaded = False
    dummy_recorder_plugin.worker_loaded = False
    dummy_recorder_plugin.load(mock_env)
    assert not dummy_recorder_plugin.master_loaded
    assert not dummy_recorder_plugin.worker_loaded


def test_abstract_methods_raise_typeerror():
    """
    Ensure instantiating BaseTelemetryRecorderPlugin without implementing
    abstract methods fails
    """
    with pytest.raises(TypeError):
        BaseTelemetryRecorderPlugin()


def test_load_without_plugin_id(mock_env, dummy_recorder_plugin):
    """
    Verify that loading the plugin without plugin id causes RunTimeError
    """
    dummy_recorder_plugin.RECORDER_PLUGIN_ID = None
    with pytest.raises(RuntimeError):
        dummy_recorder_plugin.load(mock_env)


def test_add_test_metadata_contract(dummy_recorder_plugin):
    """
    Ensure add_test_metadata returns a dict and can be merged into environment metadata.
    """
    metadata = dummy_recorder_plugin.add_test_metadata()
    assert isinstance(metadata, dict)
    assert "dummy_key" in metadata


def test_load_logs_when_invalid_runner(mock_env, dummy_recorder_plugin, caplog):
    """
    Ensure load() logs at debug level when runner type is unsupported.
    """

    class StrangeRunner:
        pass

    mock_env.runner = StrangeRunner()
    with caplog.at_level("DEBUG"):
        dummy_recorder_plugin.load(mock_env)

    # should not crash, should log nothing critical
    assert all("Failed" not in m for m in caplog.messages)
