from unittest.mock import MagicMock

import pytest

from locust_telemetry.core.exceptions import RecorderPluginError
from locust_telemetry.core.plugin import BaseRecorderPlugin


def test_load_raises_error_if_missing_plugin_id(mock_env):
    """load() must raise RecorderPluginError if RECORDER_PLUGIN_ID is not defined."""

    class NoIdPlugin(BaseRecorderPlugin):
        """Plugin missing RECORDER_PLUGIN_ID used to test error handling."""

        def add_test_metadata(self):
            return {}

        def add_cli_arguments(self, g):
            pass

        def load_master_recorders(self, env, **kw):
            pass

        def load_worker_recorders(self, env, **kw):
            pass

    plugin = NoIdPlugin()

    with pytest.raises(RecorderPluginError):
        plugin.load(mock_env)


def test_load_calls_master_loader(mock_env_master, mock_plugin):
    """
    load() must call load_master_recorders when the environment runner
    is a MasterRunner.
    """
    mock_plugin.load(mock_env_master)
    assert mock_plugin.called_master is True
    assert mock_plugin.called_worker is False


def test_load_calls_worker_loader(mock_env_worker, mock_plugin):
    """
    load() must call load_worker_recorders when the environment runner
     is a WorkerRunner.
    """
    mock_plugin.load(mock_env_worker)
    assert mock_plugin.called_worker is True
    assert mock_plugin.called_master is False


def test_add_test_metadata_is_returned(mock_plugin):
    """add_test_metadata() should return the plugin-provided metadata dictionary."""
    meta = mock_plugin.add_test_metadata()
    assert meta == {"dummy": True}


def test_add_cli_arguments_called(mock_plugin):
    """
    add_cli_arguments() should register CLI arguments on the provided group object.
    """
    group = MagicMock()
    mock_plugin.add_cli_arguments(group)
    group.add_argument.assert_called_with("--dummy")
