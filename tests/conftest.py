from typing import Any
from unittest.mock import MagicMock

import pytest
from locust.argument_parser import LocustArgumentParser
from locust.env import Environment
from locust.runners import MasterRunner

from locust_telemetry.core.manager import TelemetryPluginManager
from locust_telemetry.core.plugin import BaseTelemetryPlugin
from locust_telemetry.core.telemetry import BaseTelemetryRecorder


@pytest.fixture
def mock_env():
    env = MagicMock(
        spec=Environment,
        runner=MagicMock(),
        run_id="1234",
        parsed_options=MagicMock(
            testplan="test-plan",
            num_users=10,
            profile="default",
            wait_after_test_stop=0.1,
            recorder_interval=1,
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
def reset_singleton() -> None:
    """Reset the TelemetryPluginManager singleton before each test."""
    TelemetryPluginManager._instance = None
    TelemetryPluginManager._initialized = False


@pytest.fixture
def dummy_plugin() -> BaseTelemetryPlugin:
    """Return a fresh DummyTelemetryPlugin for testing."""

    class DummyTelemetryPlugin(BaseTelemetryPlugin):
        """Simple telemetry plugin for testing manager behavior."""

        def __init__(self) -> None:
            self.master_loaded = False
            self.worker_loaded = False
            self.added_args = False

        def add_arguments(self, parser: Any) -> None:
            self.added_args = True

        def register_master_telemetry_recorder(
            self, environment: Environment, **kwargs: Any
        ) -> None:
            self.master_loaded = True

        def register_worker_telemetry_recorder(
            self, environment: Environment, **kwargs: Any
        ) -> None:
            self.worker_loaded = True

        def load(self, environment: Environment, **kwargs: Any) -> None:
            if isinstance(environment.runner, MasterRunner):
                self.master_loaded = True
            else:
                self.worker_loaded = True

    return DummyTelemetryPlugin()


@pytest.fixture
def recorder(mock_env: Environment) -> BaseTelemetryRecorder:
    """Return a BaseTelemetryRecorder instance for testing."""
    return BaseTelemetryRecorder(env=mock_env)


@pytest.fixture
def parser() -> LocustArgumentParser:
    return LocustArgumentParser()


@pytest.fixture
def sample_metadata():
    """Return a sample metadata dict."""
    return {"run_id": "1234", "env": "staging"}
