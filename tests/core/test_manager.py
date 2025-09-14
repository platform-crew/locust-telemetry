from unittest.mock import MagicMock, patch

from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry.core.manager import TelemetryRecorderPluginManager


def test_singleton_behavior():
    """
    Ensure TelemetryRecorderPluginManager implements the singleton pattern.

    Only one instance should exist per process. Multiple instantiations
    should return the same object reference.
    """
    mgr1 = TelemetryRecorderPluginManager()
    mgr2 = TelemetryRecorderPluginManager()
    assert mgr1 is mgr2


def test_register_plugin_adds_instance(dummy_recorder_plugin):
    """
    Verify that registering a plugin adds it to the internal registry.

    Checks that the plugin instance appears in the manager's plugin list
    after registration.
    """
    mgr = TelemetryRecorderPluginManager()
    mgr.register_recorder_plugin(dummy_recorder_plugin)
    assert dummy_recorder_plugin in mgr.recorder_plugins


def test_register_plugin_avoids_duplicates(dummy_recorder_plugin):
    """
    Ensure registering the same plugin multiple times does not create duplicates.

    The manager should only store unique plugin instances, even if
    register_recorder_plugin is called more than once with the same object.
    """
    mgr = TelemetryRecorderPluginManager()
    mgr.register_recorder_plugin(dummy_recorder_plugin)
    mgr.register_recorder_plugin(dummy_recorder_plugin)
    assert mgr.recorder_plugins.count(dummy_recorder_plugin) == 1


def test_load_plugins_only_loads_enabled(mock_env, dummy_recorder_plugin):
    """
    Verify that only plugins listed in enable_telemetry_plugin are loaded.

    - MasterRunner triggers master recorder.
    - WorkerRunner triggers worker recorder.
    - Disabled plugins are skipped.
    """
    mgr = TelemetryRecorderPluginManager()
    mgr.register_recorder_plugin(dummy_recorder_plugin)

    # Master runner
    mock_env.runner.__class__ = MasterRunner
    mock_env.parsed_options.enable_telemetry_recorder = ["dummy"]
    mgr.load_recorder_plugins(mock_env)
    assert dummy_recorder_plugin.master_loaded is True
    assert dummy_recorder_plugin.worker_loaded is False

    # Worker runner
    dummy_recorder_plugin.master_loaded = dummy_recorder_plugin.worker_loaded = False
    mock_env.runner.__class__ = WorkerRunner
    mock_env.parsed_options.enable_telemetry_recorder = ["dummy"]
    mgr.load_recorder_plugins(mock_env)
    assert dummy_recorder_plugin.master_loaded is False
    assert dummy_recorder_plugin.worker_loaded is True

    # Plugin not enabled
    dummy_recorder_plugin.master_loaded = dummy_recorder_plugin.worker_loaded = False
    mock_env.parsed_options.enable_telemetry_recorder = ["other"]
    mgr.load_recorder_plugins(mock_env)
    assert dummy_recorder_plugin.master_loaded is False
    assert dummy_recorder_plugin.worker_loaded is False


def test_load_plugins_no_enabled_plugins(mock_env, dummy_recorder_plugin):
    """
    Ensure that if no plugins are enabled, load_plugins does not invoke any plugin.

    This simulates the scenario where the user has not provided
    any --enable-telemetry-plugin CLI arguments.
    """
    mgr = TelemetryRecorderPluginManager()
    mgr.register_recorder_plugin(dummy_recorder_plugin)

    mock_env.parsed_options.enable_telemetry_plugin = None
    mgr.load_recorder_plugins(mock_env)
    assert (
        not dummy_recorder_plugin.master_loaded
        and not dummy_recorder_plugin.worker_loaded
    )


def test_load_plugins_logs_enabled_plugins(caplog, mock_env, dummy_recorder_plugin):
    """
    Ensure that load_recorder_plugins logs the enabled plugins.
    """
    mgr = TelemetryRecorderPluginManager()
    mgr.register_recorder_plugin(dummy_recorder_plugin)

    mock_env.runner.__class__ = MasterRunner
    mock_env.parsed_options.enable_telemetry_recorder = ["dummy"]

    with caplog.at_level("INFO"):
        mgr.load_recorder_plugins(mock_env)

    assert any("Following recorders are enabled" in msg for msg in caplog.messages)


def test_load_plugins_handles_plugin_exception(
    caplog, mock_env, dummy_recorder_plugin, monkeypatch
):
    """
    Verify that if a plugin raises during load, the manager logs the exception.
    """
    mgr = TelemetryRecorderPluginManager()

    # Replace plugin.load with a failing one
    def failing_load(*args, **kwargs):
        raise RuntimeError("boom")

    dummy_recorder_plugin.load = failing_load
    mgr.register_recorder_plugin(dummy_recorder_plugin)

    mock_env.runner.__class__ = MasterRunner
    mock_env.parsed_options.enable_telemetry_recorder = ["dummy"]

    with caplog.at_level("ERROR"):
        mgr.load_recorder_plugins(mock_env)

    assert any("Failed to load recorder plugin" in msg for msg in caplog.messages)


def test_register_plugin_clis_invokes_plugin_method(dummy_recorder_plugin):
    """
    Ensure that register_plugin_clis calls add_cli_arguments on all plugins.
    """
    mgr = TelemetryRecorderPluginManager()
    dummy_recorder_plugin.add_cli_arguments = MagicMock()
    mgr.register_recorder_plugin(dummy_recorder_plugin)

    fake_group = MagicMock()
    mgr.register_plugin_clis(fake_group)

    dummy_recorder_plugin.add_cli_arguments.assert_called_once_with(fake_group)


def test_register_plugin_metadata_merges_and_sets(
    monkeypatch, mock_env, dummy_recorder_plugin
):
    """
    Ensure metadata from all plugins is merged and applied to the environment.
    """
    mgr = TelemetryRecorderPluginManager()
    dummy_recorder_plugin.add_test_metadata = MagicMock(
        return_value={"plugin_key": "plugin_value"}
    )
    mgr.register_recorder_plugin(dummy_recorder_plugin)

    # Patch set_test_metadata to spy on it
    with patch("locust_telemetry.core.manager.set_test_metadata") as mock_set:
        metadata = mgr.register_plugin_metadata(mock_env)

    # DEFAULT_ENVIRONMENT_METADATA comes from config, so plugin updates it
    assert "plugin_key" in metadata
    mock_set.assert_called_once_with(mock_env, metadata)


def test_register_plugin_metadata_handles_empty_plugins(monkeypatch, mock_env):
    """
    If no plugins are registered, metadata should equal DEFAULT_ENVIRONMENT_METADATA.
    """
    mgr = TelemetryRecorderPluginManager()

    with patch(
        "locust_telemetry.core.manager.config.DEFAULT_ENVIRONMENT_METADATA",
        {"foo": "bar"},
    ):
        with patch("locust_telemetry.core.manager.set_test_metadata") as mock_set:
            metadata = mgr.register_plugin_metadata(mock_env)

    assert metadata == {"foo": "bar"}
    mock_set.assert_called_once_with(mock_env, {"foo": "bar"})
