import time

from locust.runners import MasterRunner, WorkerRunner

from locust_telemetry.core.recorder import TelemetryBaseRecorder


def test_initialization_sets_env_and_metadata(recorder, mock_env):
    """
    Ensure TelemetryRecorderBase initializes environment, username, hostname, and pid.
    """
    assert recorder.env is mock_env
    assert hasattr(recorder, "_username")
    assert hasattr(recorder, "_hostname")
    assert hasattr(recorder, "_pid")


def test_recorder_context(recorder, mock_env):
    """
    Verify if the created recorder context is correct or not
    """
    mock_env.runner.__class__ = MasterRunner
    context = recorder.recorder_context()
    assert context["run_id"] == mock_env.telemetry_meta.run_id
    assert context["testplan"] == mock_env.parsed_options.testplan
    assert context["recorder"] == recorder.name
    assert context["source"] == mock_env.runner.__class__.__name__
    assert context["source_id"] == "master"

    mock_env.runner.__class__ = WorkerRunner
    context = recorder.recorder_context()
    assert context["run_id"] == mock_env.telemetry_meta.run_id
    assert context["testplan"] == mock_env.parsed_options.testplan
    assert context["recorder"] == recorder.name
    assert context["source"] == mock_env.runner.__class__.__name__
    assert context["source_id"] == f"worker-{mock_env.runner.worker_index}"


def test_default_name_classvar():
    """Ensure the default recorder name is 'base'."""
    assert TelemetryBaseRecorder.name == "base"


def test_recorder_property_now_ms(recorder):
    """Verify if the recorder property now_ms returns as expected"""
    ms1 = recorder.now_ms
    time.sleep(0.3)
    ms2 = recorder.now_ms
    assert isinstance(ms1, int)
    assert isinstance(ms2, int)
    assert ms1 != ms2
