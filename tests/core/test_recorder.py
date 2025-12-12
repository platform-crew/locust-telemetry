from conftest import (
    DummyLifecycleHandler,
    DummyOutputHandler,
    DummyRequestHandler,
    DummySystemHandler,
)

from locust_telemetry.core.recorder import (
    BaseRecorder,
    MasterNodeRecorder,
    WorkerNodeRecorder,
)


def test_base_recorder_initializes_handlers(mock_env):
    """BaseRecorder should initialize all handler classes correctly."""
    recorder = BaseRecorder(
        env=mock_env,
        output_handler_cls=DummyOutputHandler,
        lifecycle_handler_cls=DummyLifecycleHandler,
        system_handler_cls=DummySystemHandler,
        requests_handler_cls=DummyRequestHandler,
    )

    assert isinstance(recorder.output, DummyOutputHandler)
    assert isinstance(recorder.lifecycle, DummyLifecycleHandler)
    assert isinstance(recorder.system, DummySystemHandler)
    assert isinstance(recorder.requests, DummyRequestHandler)


def test_base_recorder_cpu_warning_forwards_to_lifecycle(mock_env):
    """on_cpu_warning should forward CPU usage to the lifecycle handler."""
    recorder = BaseRecorder(
        env=mock_env,
        output_handler_cls=DummyOutputHandler,
        lifecycle_handler_cls=DummyLifecycleHandler,
        system_handler_cls=DummySystemHandler,
        requests_handler_cls=DummyRequestHandler,
    )

    recorder.on_cpu_warning(cpu_usage=87)

    assert recorder.lifecycle.called == [("cpu", {"value": 87, "unit": "percent"})]


def test_master_recorder_registers_events(mock_env):
    """MasterNodeRecorder should register master-specific event listeners."""
    MasterNodeRecorder(
        mock_env,
        DummyOutputHandler,
        DummyLifecycleHandler,
        DummySystemHandler,
        DummyRequestHandler,
    )

    mock_env.events.test_start.add_listener.assert_called()
    mock_env.events.test_stop.add_listener.assert_called()
    mock_env.events.spawning_complete.add_listener.assert_called()


def test_master_on_test_start(mock_env):
    """
    MasterNodeRecorder.on_test_start should start all handlers and register lifecycle.
    """
    recorder = MasterNodeRecorder(
        mock_env,
        DummyOutputHandler,
        DummyLifecycleHandler,
        DummySystemHandler,
        DummyRequestHandler,
    )

    recorder.on_test_start()

    assert recorder.lifecycle.called == ["test_start"]
    assert recorder.system.started is True
    assert recorder.requests.started is True


def test_master_on_test_stop(mock_env):
    """MasterNodeRecorder.on_test_stop should stop all handlers and record lifecycle."""
    recorder = MasterNodeRecorder(
        mock_env,
        DummyOutputHandler,
        DummyLifecycleHandler,
        DummySystemHandler,
        DummyRequestHandler,
    )

    recorder.on_test_stop()

    assert recorder.lifecycle.called == ["test_stop"]
    assert recorder.system.stopped is True
    assert recorder.requests.stopped is True


def test_master_on_spawning_complete(mock_env):
    """
    MasterNodeRecorder.on_spawning_complete should forward user count to lifecycle.
    """
    recorder = MasterNodeRecorder(
        mock_env,
        DummyOutputHandler,
        DummyLifecycleHandler,
        DummySystemHandler,
        DummyRequestHandler,
    )

    recorder.on_spawning_complete(user_count=50)

    assert recorder.lifecycle.called == [("spawn", {"user_count": 50})]


def test_worker_on_test_start(mock_env):
    """
    WorkerNodeRecorder.on_test_start should start system and requests but not lifecycle.
    """
    recorder = WorkerNodeRecorder(
        mock_env,
        DummyOutputHandler,
        DummyLifecycleHandler,
        DummySystemHandler,
        DummyRequestHandler,
    )

    recorder.on_test_start()

    assert recorder.system.started is True
    assert recorder.requests.started is True
    assert recorder.lifecycle.called == []


def test_worker_on_test_stop(mock_env):
    """
    WorkerNodeRecorder.on_test_stop should stop system and requests but not lifecycle.
    """
    recorder = WorkerNodeRecorder(
        mock_env,
        DummyOutputHandler,
        DummyLifecycleHandler,
        DummySystemHandler,
        DummyRequestHandler,
    )

    recorder.on_test_stop()

    assert recorder.system.stopped is True
    assert recorder.requests.stopped is True
    assert recorder.lifecycle.called == []
