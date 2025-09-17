from typing import Any, Type
from unittest.mock import MagicMock

import pytest
from locust.argument_parser import LocustArgumentParser
from locust.env import Environment

from locust_telemetry.core.coordinator import TelemetryCoordinator
from locust_telemetry.core.manager import TelemetryRecorderPluginManager
from locust_telemetry.core.plugin import BaseTelemetryRecorderPlugin
from locust_telemetry.core.recorder import TelemetryBaseRecorder
from locust_telemetry.recorders.json.master import (
    MasterLocustJsonTelemetryRecorder,
)


class DummyTelemetryRecorderPlugin(BaseTelemetryRecorderPlugin):
    """Simple telemetry recorder plugin for testing manager behavior."""

    RECORDER_PLUGIN_ID = "dummy"

    def __init__(self) -> None:
        self.master_loaded = False
        self.worker_loaded = False
        self.added_cli_args = False

    def add_test_metadata(self):
        return {"dummy_key": "dummy_value"}

    def add_cli_arguments(self, group) -> None:
        self.added_cli_args = True

    def load_master_telemetry_recorders(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        self.master_loaded = True

    def load_worker_telemetry_recorders(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        self.worker_loaded = True


@pytest.fixture
def mock_env():
    env = MagicMock(
        spec=Environment,
        runner=MagicMock(),
        telemetry_meta=MagicMock(run_id="1234"),
        parsed_options=MagicMock(
            testplan="test-plan",
            num_users=10,
            profile="default",
            wait_after_test_stop=0.1,
            lt_stats_recorder_interval=1,
        ),
        stats=MagicMock(total=MagicMock(), entries={}, errors={}),
        events=MagicMock(),
    )

    for event_name in ["test_start", "test_stop", "spawning_complete"]:
        event_mock = MagicMock()
        setattr(env.events, event_name, event_mock)
        event_mock.add_listener = MagicMock()
    return env


@pytest.fixture(autouse=True)
def reset_coordinator_singleton() -> None:
    """Reset the TelemetryCoordinator singleton before each test."""
    TelemetryCoordinator._instance = None
    TelemetryCoordinator._initialized = False


@pytest.fixture
def dummy_recorder_plugin_class() -> Type[DummyTelemetryRecorderPlugin]:
    """Return a fresh DummyTelemetryRecorderPlugin class for testing."""
    return DummyTelemetryRecorderPlugin


@pytest.fixture
def dummy_recorder_plugin() -> BaseTelemetryRecorderPlugin:
    """Return a fresh DummyTelemetryRecorderPlugin instance for testing."""
    return DummyTelemetryRecorderPlugin()


@pytest.fixture
def env_with_runner():
    """Create a real Locust environment with a runner and parsed options."""
    env = Environment()
    env.create_local_runner()  # ensures runner is available
    env.parsed_options = MagicMock()
    env.parsed_options.testplan = "test-plan"
    return env


@pytest.fixture
def recorder(mock_env: Environment) -> TelemetryBaseRecorder:
    """Return a TelemetryBaseRecorder instance for testing."""
    return TelemetryBaseRecorder(env=mock_env)


@pytest.fixture
def parser() -> LocustArgumentParser:
    """Return a fresh Locust argument parser for testing CLI integration."""
    return LocustArgumentParser()


@pytest.fixture
def sample_metadata():
    """Return a sample test metadata dictionary."""
    return {"run_id": "1234", "env": "staging"}


@pytest.fixture(autouse=True)
def reset_manager_singleton():
    """Reset singleton between tests to avoid state leakage."""
    TelemetryRecorderPluginManager._instance = None
    TelemetryRecorderPluginManager._initialized = False
    yield
    TelemetryRecorderPluginManager._instance = None
    TelemetryRecorderPluginManager._initialized = False


@pytest.fixture
def master_json_recorder(mock_env):
    """Return a json stats master recorder"""
    return MasterLocustJsonTelemetryRecorder(env=mock_env)
