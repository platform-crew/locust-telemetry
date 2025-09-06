"""
Tests for locust_observability.initialization module.

Verifies:
- CLI argument registration
- Logging setup
- Master and worker initialization behavior
"""

from unittest.mock import MagicMock, patch

from locust.argument_parser import LocustArgumentParser
from locust.runners import MasterRunner, WorkerRunner

from locust_observability import config, initialization


def test_add_arguments(monkeypatch):
    """
    Test that locust-observability CLI arguments are correctly added
    and default values are respected.
    """
    parser = LocustArgumentParser()
    initialization.add_arguments(parser)

    # Parse minimal required arguments
    args = parser.parse_args(["--testplan", "myplan"])

    assert args.testplan == "myplan"
    assert args.recorder_interval == config.DEFAULT_OB_RECORDER_INTERVAL
    assert args.wait_after_test_stop == config.DEFAULT_OB_WAIT_AFTER_TEST_STOP


@patch("locust_observability.initialization.configure_logging")
def test_setup_logging(mock_configure_logging, mock_env):
    """
    Test that setup_logging configures logging for the environment
    and calls configure_logging.
    """
    env = mock_env
    env.runner.__class__.__name__ = "MasterRunner"

    initialization.setup_logging(env)

    mock_configure_logging.assert_called_once()


def test_setup_master_test_calls_recorders(monkeypatch, mock_env):
    """
    Test that setup_master_test:
    - Calls all master node recorders
    - Sends metadata message to workers
    """
    env = mock_env
    env.runner = MagicMock(spec=MasterRunner)

    # Patch MASTER_NODE_RECORDERS with a mock recorder
    recorder_mock = MagicMock()
    monkeypatch.setattr(config, "MASTER_NODE_RECORDERS", [recorder_mock])

    initialization.setup_master_test(env)

    recorder_mock.assert_called_once_with(env=env)
    env.runner.send_message.assert_called_once_with(
        "set_metadata", {"run_id": env.run_id}
    )


def test_setup_master_test_skips_non_master_runner(monkeypatch, mock_env):
    """
    Verify that setup_master_test does nothing when the environment
    runner is not a MasterRunner.
    """
    env = mock_env
    env.runner = MagicMock(spec=WorkerRunner)

    recorder_mock = MagicMock()
    monkeypatch.setattr(config, "MASTER_NODE_RECORDERS", [recorder_mock])

    initialization.setup_master_test(env)

    recorder_mock.assert_not_called()
    env.runner.send_message.assert_not_called()


def test_init_worker_skips_non_worker_runner(monkeypatch, mock_env):
    """
    Ensure init_worker does nothing if the environment runner is not a WorkerRunner.
    """
    env = mock_env
    register_message_mock = MagicMock()
    env.runner = MagicMock(spec=MasterRunner, register_message=register_message_mock)

    initialization.init_worker(env)

    # register_message should not be called
    register_message_mock.assert_not_called()


def test_init_worker_registers_message(monkeypatch, mock_env):
    """
    Test that init_worker:
    - Registers the 'set_metadata' message
    - Calls handle_worker_metadata when the message is received
    """
    env = mock_env
    env.runner = MagicMock(spec=WorkerRunner)

    handle_worker_mock = MagicMock()
    monkeypatch.setattr(initialization, "handle_worker_metadata", handle_worker_mock)

    initialization.init_worker(env)

    # Ensure register_message was called
    env.runner.register_message.assert_called_once()
    args, _ = env.runner.register_message.call_args

    # The first argument is the message name
    assert args[0] == "set_metadata"

    # The second argument is the lambda callback
    lambda_func = args[1]

    # Simulate a message being received
    msg = MagicMock()
    msg.data = {"run_id": "123"}
    lambda_func(msg)

    handle_worker_mock.assert_called_once_with(env, {"run_id": "123"})
