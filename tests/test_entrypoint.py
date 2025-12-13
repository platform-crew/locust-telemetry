from unittest.mock import MagicMock

from locust_telemetry import entrypoint


def test_initialize_calls(monkeypatch):
    """
    Verify that initialize registers the default plugin and starts the coordinator.
    """
    # Patch TelemetryCoordinator
    coordinator_mock = MagicMock()
    monkeypatch.setattr(entrypoint, "TelemetryCoordinator", coordinator_mock)

    # Patch TelemetryRecorderPluginManager
    plugin_manager_mock = MagicMock()
    monkeypatch.setattr(
        entrypoint, "RecorderPluginManager", lambda: plugin_manager_mock
    )

    # Patch CONFIGURED_RECORDER_PLUGINS to use a fake plugin class
    plugin_instance_mock = MagicMock()
    plugin_class_mock = MagicMock(return_value=plugin_instance_mock)
    monkeypatch.setattr(entrypoint, "CONFIGURED_RECORDER_PLUGINS", (plugin_class_mock,))

    # Call initialize
    entrypoint.initialize()

    # Assert coordinator initialized with plugin manager
    coordinator_mock.assert_called_once_with(
        recorder_plugin_manager=plugin_manager_mock
    )

    # Assert recorder plugin was registered
    plugin_manager_mock.register_recorder_plugin.assert_called_once_with(
        plugin_instance_mock
    )

    # Assert coordinator.initialize() was called
    coordinator_mock.return_value.initialize.assert_called_once()


def test_setup_telemetry_calls_initialize(monkeypatch):
    """
    Verify that setup_telemetry calls initialize internally.
    """
    initialize_mock = MagicMock()
    monkeypatch.setattr(entrypoint, "initialize", initialize_mock)

    entrypoint.setup_telemetry()

    initialize_mock.assert_called_once()
