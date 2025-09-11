from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry.core.manager import (
    TelemetryRecorderPluginManager,
    telemetry_recorder_plugin,
)


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
    mock_env.parsed_options.enable_telemetry_plugin = ["dummy"]
    mgr.load_recorder_plugins(mock_env)
    assert dummy_recorder_plugin.master_loaded is True
    assert dummy_recorder_plugin.worker_loaded is False

    # Worker runner
    dummy_recorder_plugin.master_loaded = dummy_recorder_plugin.worker_loaded = False
    mock_env.runner.__class__ = WorkerRunner
    mock_env.parsed_options.enable_telemetry_plugin = ["dummy"]
    mgr.load_recorder_plugins(mock_env)
    assert dummy_recorder_plugin.master_loaded is False
    assert dummy_recorder_plugin.worker_loaded is True

    # Plugin not enabled
    dummy_recorder_plugin.master_loaded = dummy_recorder_plugin.worker_loaded = False
    mock_env.parsed_options.enable_telemetry_plugin = ["other"]
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


def test_telemetry_plugin_decorator_registers_class(dummy_recorder_plugin_class):
    """
    Verify that the @telemetry_plugin decorator auto-registers a plugin.

    When a class is decorated with @telemetry_plugin, an instance
    should be automatically added to TelemetryRecorderPluginManager's registry.
    """

    @telemetry_recorder_plugin
    class AutoRegisteredPlugin(dummy_recorder_plugin_class):
        pass

    mgr = TelemetryRecorderPluginManager()
    found = any(isinstance(p, AutoRegisteredPlugin) for p in mgr.recorder_plugins)
    assert found
