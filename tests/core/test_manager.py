from unittest.mock import MagicMock, patch

import pytest

from locust_telemetry.core.exceptions import (
    RecorderPluginAlreadyRegistered,
    RecorderPluginLoadError,
)
from locust_telemetry.core.manager import RecorderPluginManager


def test_singleton_behavior():
    """Ensure RecorderPluginManager behaves as a singleton."""
    m1 = RecorderPluginManager()
    m2 = RecorderPluginManager()
    assert m1 is m2


def test_register_plugin_success(recorder_plugin_manager, mock_recorder_plugin):
    """Verify a plugin can be registered successfully."""
    recorder_plugin_manager.register_recorder_plugin(mock_recorder_plugin)
    assert mock_recorder_plugin in recorder_plugin_manager.recorder_plugins


def test_register_plugin_duplicate_raises(
    recorder_plugin_manager, mock_recorder_plugin
):
    """Ensure duplicate plugin registration raises an exception."""
    recorder_plugin_manager.register_recorder_plugin(mock_recorder_plugin)
    with pytest.raises(RecorderPluginAlreadyRegistered):
        recorder_plugin_manager.register_recorder_plugin(mock_recorder_plugin)


def test_register_plugin_clis(recorder_plugin_manager, mock_recorder_plugin):
    """Confirm CLI arguments are registered for all plugins."""
    recorder_plugin_manager.register_recorder_plugin(mock_recorder_plugin)
    group = MagicMock()
    recorder_plugin_manager.register_plugin_clis(group)
    mock_recorder_plugin.add_cli_arguments.assert_called_once_with(group)


@patch(
    "locust_telemetry.core.manager.config.DEFAULT_ENVIRONMENT_METADATA",
    {"default": "meta"},
)
@patch("locust_telemetry.core.manager.set_test_metadata")
def test_register_plugin_metadata(
    mock_set_meta, recorder_plugin_manager, mock_recorder_plugin
):
    """Test metadata aggregation and environment assignment."""
    recorder_plugin_manager.register_recorder_plugin(mock_recorder_plugin)

    env = MagicMock()
    metadata = recorder_plugin_manager.register_plugin_metadata(env)

    mock_recorder_plugin.add_test_metadata.assert_called_once()
    mock_set_meta.assert_called_once_with(env, {"default": "meta", "extra": "value"})
    assert metadata == {"default": "meta", "extra": "value"}


def test_load_recorder_plugins_success(recorder_plugin_manager, mock_recorder_plugin):
    """Ensure enabled plugins are loaded successfully."""
    recorder_plugin_manager.register_recorder_plugin(mock_recorder_plugin)

    env = MagicMock()
    env.parsed_options.enable_telemetry_recorder = ["mock_recorder"]

    recorder_plugin_manager.load_recorder_plugins(env)
    mock_recorder_plugin.load.assert_called_once_with(environment=env)


def test_load_recorder_plugins_skips_disabled(
    recorder_plugin_manager, mock_recorder_plugin
):
    """Verify disabled plugins are skipped during loading."""
    recorder_plugin_manager.register_recorder_plugin(mock_recorder_plugin)

    env = MagicMock()
    env.parsed_options.enable_telemetry_recorder = ["another_recorder"]

    recorder_plugin_manager.load_recorder_plugins(env)
    mock_recorder_plugin.load.assert_not_called()


def test_load_recorder_plugins_raises_on_failure(
    recorder_plugin_manager, mock_recorder_plugin
):
    """Check that plugin load errors are wrapped in RecorderPluginLoadError."""
    recorder_plugin_manager.register_recorder_plugin(mock_recorder_plugin)

    env = MagicMock()
    env.parsed_options.enable_telemetry_recorder = ["mock_recorder"]
    mock_recorder_plugin.load.side_effect = Exception("boom")

    with pytest.raises(RecorderPluginLoadError):
        recorder_plugin_manager.load_recorder_plugins(env)
