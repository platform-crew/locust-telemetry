"""
Tests for Locust Telemetry Entrypoint
"""

from unittest.mock import MagicMock

from locust_telemetry import entrypoint


def test_initialize_calls(monkeypatch):
    """
    Verify that initialize calls configure_logging and starts the orchestrator.
    """
    # Patch TelemetryCoordinator
    coordinator_mock = MagicMock()
    monkeypatch.setattr(entrypoint, "TelemetryCoordinator", coordinator_mock)

    # Patch TelemetryRecorderPluginManager so orchestrator is initialized with it
    plugin_manager_mock = MagicMock()
    monkeypatch.setattr(
        entrypoint, "TelemetryRecorderPluginManager", lambda: plugin_manager_mock
    )

    # Call initialize
    entrypoint.initialize()

    # Assert orchestrator was initialized with the plugin manager
    coordinator_mock.assert_called_once_with(
        recorder_plugin_manager=plugin_manager_mock
    )

    # Assert orchestrator.initialize() was called
    coordinator_mock.return_value.initialize.assert_called_once()


def test_setup_telemetry_calls_initialize(monkeypatch):
    """
    Verify that setup_telemetry calls initialize internally.
    """
    initialize_mock = MagicMock()
    monkeypatch.setattr(entrypoint, "initialize", initialize_mock)

    entrypoint.setup_telemetry()

    initialize_mock.assert_called_once()
