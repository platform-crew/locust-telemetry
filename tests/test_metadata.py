"""
Tests for locust_observability.metadata module.

Verifies:
- Generating test metadata
- Setting metadata on the environment
- Handling metadata in worker nodes
"""

from unittest.mock import MagicMock

from locust_observability import config, metadata


def test_get_test_metadata_returns_dict_with_run_id():
    """
    Ensure get_test_metadata returns a dictionary containing a 'run_id' key
    with a valid ISO-formatted UTC timestamp.
    """
    result = metadata.get_test_metadata()
    assert isinstance(result, dict)
    assert "run_id" in result
    # Ensure it's a string in ISO format
    assert "T" in result["run_id"] and result["run_id"].endswith("Z") is False


def test_set_test_metadata_adds_attributes_to_environment(mock_env):
    """
    Ensure set_test_metadata sets each key/value pair from metadata as attributes
    on the environment.
    """
    env = mock_env
    data = {"run_id": "123", "custom_key": "value"}

    metadata.set_test_metadata(env, data)

    assert env.run_id == "123"
    assert env.custom_key == "value"


def test_handle_worker_metadata_calls_set_and_worker_recorders(monkeypatch, mock_env):
    """
    Ensure handle_worker_metadata:
    - Calls set_test_metadata
    - Calls all worker node recorders with env
    - Logs the applied metadata
    """
    env = mock_env
    env.parsed_options.testplan = "my-testplan"
    env.run_id = "123"

    # Patch WORKER_NODE_RECORDERS with a mock recorder
    recorder_mock = MagicMock()
    monkeypatch.setattr(config, "WORKER_NODE_RECORDERS", [recorder_mock])

    # Patch set_test_metadata to track call
    set_test_mock = MagicMock()
    monkeypatch.setattr(metadata, "set_test_metadata", set_test_mock)

    # Patch logger to capture logging
    log_mock = MagicMock()
    monkeypatch.setattr(metadata.logger, "info", log_mock)

    # Call the function
    metadata.handle_worker_metadata(env, {"run_id": "123"})

    set_test_mock.assert_called_once_with(env, {"run_id": "123"})
    recorder_mock.assert_called_once_with(env=env)
    log_mock.assert_called_once_with(
        "[Worker] Metadata applied: run_id=%s, testplan=%s", "123", "my-testplan"
    )


def test_handle_worker_metadata_handles_missing_testplan(monkeypatch, mock_env):
    """
    Verify that handle_worker_metadata works even if environment.parsed_options
    has no 'testplan' attribute.
    """
    env = mock_env
    env.run_id = "123"
    env.parsed_options = MagicMock()
    del env.parsed_options.testplan  # simulate missing attribute

    recorder_mock = MagicMock()
    monkeypatch.setattr(config, "WORKER_NODE_RECORDERS", [recorder_mock])
    monkeypatch.setattr(metadata, "set_test_metadata", MagicMock())
    log_mock = MagicMock()
    monkeypatch.setattr(metadata.logger, "info", log_mock)

    metadata.handle_worker_metadata(env, {"run_id": "123"})

    recorder_mock.assert_called_once_with(env=env)
    # testplan is None
    log_mock.assert_called_once_with(
        "[Worker] Metadata applied: run_id=%s, testplan=%s", "123", None
    )
