import importlib
import logging
from unittest.mock import MagicMock

import pytest
from locust.argument_parser import LocustArgumentParser
from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry.core.coordinator import TelemetryCoordinator
from locust_telemetry.core.handlers import (
    BaseLifecycleHandler,
    BaseOutputHandler,
    BaseRequestHandler,
    BaseSystemMetricsHandler,
)
from locust_telemetry.core.manager import RecorderPluginManager
from locust_telemetry.core.plugin import BaseRecorderPlugin
from locust_telemetry.recorders.json.handlers import JsonTelemetryOutputHandler
from locust_telemetry.recorders.otel.handlers import OtelOutputHandler
from locust_telemetry.recorders.otel.otel import InstrumentRegistry


class DummyOutputHandler(BaseOutputHandler):
    """Concrete OutputHandler for testing, implements all abstract methods."""

    def __init__(self, env: Environment):
        super().__init__(env)
        self.events = []

    def record_event(self, tl_type, *args, **kwargs):
        self.events.append(("event", tl_type, args, kwargs))

    def record_metrics(self, tl_type, *args, **kwargs):
        self.events.append(("metric", tl_type, args, kwargs))


class DummyLifecycleHandler(BaseLifecycleHandler):
    """Concrete LifecycleHandler for testing."""

    def __init__(self, output: BaseOutputHandler, env: Environment):
        super().__init__(output, env)
        self.called = []

    def on_test_start(self):
        self.called.append("test_start")

    def on_test_stop(self):
        self.called.append("test_stop")

    def on_spawning_complete(self, *args, **kwargs):
        self.called.append(("spawn", kwargs))

    def on_cpu_warning(self, *args, **kwargs):
        self.called.append(("cpu", kwargs))


class DummySystemHandler(BaseSystemMetricsHandler):
    """Concrete SystemMetricsHandler for testing."""

    def __init__(self, output: BaseOutputHandler, env: Environment):
        super().__init__(output, env)
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True


class DummyRequestHandler(BaseRequestHandler):
    """Concrete RequestHandler for testing."""

    def __init__(self, output: BaseOutputHandler, env: Environment):
        super().__init__(output, env)
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True

    def on_request(self, *args, **kwargs):
        pass


class DummyPlugin(BaseRecorderPlugin):
    """A simple concrete plugin used to test BaseRecorderPlugin behavior."""

    RECORDER_PLUGIN_ID = "dummy"

    def __init__(self):
        self.called_master = False
        self.called_worker = False

    def add_test_metadata(self):
        """Return a sample metadata dict."""
        return {"dummy": True}

    def add_cli_arguments(self, group):
        """Register a dummy CLI argument."""
        group.add_argument("--dummy")

    def load_master_recorders(self, environment, **kwargs):
        """Mark that master recorders were initialized."""
        self.called_master = True

    def load_worker_recorders(self, environment, **kwargs):
        """Mark that worker recorders were initialized."""
        self.called_worker = True


def _mock_env():
    env = MagicMock(
        spec=Environment,
        runner=MagicMock(),
        telemetry_meta=MagicMock(run_id="1234"),
        parsed_options=MagicMock(
            testplan="test-plan",
            num_users=10,
            profile="default",
            lt_stats_recorder_interval=1,
        ),
        stats=MagicMock(total=MagicMock(), entries={}, errors={}),
        events=MagicMock(),
        add_listener=MagicMock(),
    )
    return env


@pytest.fixture
def mock_plugin() -> DummyPlugin:
    return DummyPlugin()


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
            lt_stats_recorder_interval=1,
        ),
        stats=MagicMock(total=MagicMock(), entries={}, errors={}),
        events=MagicMock(),
        add_listener=MagicMock(),
    )
    return env


@pytest.fixture
def mock_env_master():
    """Return mock environment with master runner"""
    mock_env = _mock_env()
    mock_env.runner = MagicMock(spec=MasterRunner)
    return mock_env


@pytest.fixture
def mock_env_worker():
    """Return mock environment with worker runner"""
    mock_env = _mock_env()
    mock_env.runner = MagicMock(spec=WorkerRunner, worker_index=2)
    return mock_env


@pytest.fixture
def mock_otel_env(mock_env):
    """
    Mock Locust environment with a real InstrumentRegistry
    backed by a mocked OTEL meter.
    """
    # Mock OTEL meter
    meter = MagicMock()
    registry = InstrumentRegistry(meter=meter)
    mock_env.otel_registry = registry
    mock_env.runner.user_count = 10
    return mock_env


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
    RecorderPluginManager._instance = TelemetryCoordinator._instance = None
    RecorderPluginManager._initialized = TelemetryCoordinator._initialized = False
    yield
    RecorderPluginManager._instance = TelemetryCoordinator._instance = None
    RecorderPluginManager._initialized = TelemetryCoordinator._initialized = False


@pytest.fixture(autouse=True)
def reset_logging(monkeypatch):
    """Reset logging between tests to avoid interference."""
    logging.shutdown()
    importlib.reload(logging)
    yield


@pytest.fixture
def recorder_plugin_manager():
    """Return a fresh RecorderPluginManager instance."""
    return RecorderPluginManager()


@pytest.fixture
def mock_recorder_plugin():
    """Create a mock recorder plugin with standard attributes."""
    plugin = MagicMock()
    plugin.RECORDER_PLUGIN_ID = "mock_recorder"
    plugin.__class__.__name__ = "MockRecorderPlugin"
    plugin.add_cli_arguments = MagicMock()
    plugin.add_test_metadata = MagicMock(return_value={"extra": "value"})
    plugin.load = MagicMock()
    return plugin


@pytest.fixture
def json_output_handler(mock_env):
    """Create a JsonTelemetryOutputHandler with mocked context."""
    h = JsonTelemetryOutputHandler(env=mock_env)
    h.get_context = MagicMock(return_value={"context": 1})
    return h


@pytest.fixture
def otel_output_handler(mock_env):
    """
    OtelOutputHandler with patched get_context().
    """
    handler = OtelOutputHandler(mock_env)
    handler.get_context = MagicMock(return_value={"ctx": "test"})
    return handler
