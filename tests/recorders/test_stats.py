"""
Tests for MasterNodeStatsRecorder

These tests cover initialization, event handling, and helper methods
for the MasterNodeStatsRecorder in Locust-Observability.
"""

import logging
import os
import socket
from unittest.mock import MagicMock, patch

import gevent

from locust_observability.metrics import EventsEnum
from locust_observability.recorders.stats import MasterNodeStatsRecorder


def test_master_recorder_init_registers_listeners(mock_env):
    """
    Verify that initializing MasterNodeStatsRecorder sets basic attributes.
    """
    recorder = MasterNodeStatsRecorder(mock_env)

    assert recorder._username == os.getenv("USER", "unknown")
    assert recorder._hostname == socket.gethostname()
    assert isinstance(recorder._pid, int)


@patch("locust_observability.recorders.stats.gevent.spawn")
@patch.object(MasterNodeStatsRecorder, "log_metrics")
def test_on_test_start_spawns_logger_and_logs(mock_log, mock_spawn, mock_env):
    """
    Test that on_test_start spawns the greenlet logger and logs the start event.
    """
    recorder = MasterNodeStatsRecorder(mock_env)
    recorder.on_test_start()

    mock_spawn.assert_called_once_with(recorder._log_request_stats)
    mock_log.assert_called_once_with(
        metric=EventsEnum.TEST_START_EVENT.value,
        num_clients=10,
        profile_name="default",
        username=recorder._username,
    )


def test_log_request_stats_handles_greenlet_exit(monkeypatch, mock_env, caplog):
    """
    Ensure _log_request_stats stops cleanly when GreenletExit is raised.
    """
    recorder = MasterNodeStatsRecorder(mock_env)

    # Replace _log_total_stats to raise GreenletExit
    def raise_greenlet_exit(*args, **kwargs):
        raise gevent.GreenletExit

    monkeypatch.setattr(recorder, "_log_total_stats", raise_greenlet_exit)

    # Capture logging
    with caplog.at_level(logging.INFO):
        recorder._log_request_stats()

    # Verify that GreenletExit was caught and logged
    assert any(
        "Request stats logger stopped cleanly" in record.message
        for record in caplog.records
    )


@patch("time.sleep", return_value=None)
@patch.object(MasterNodeStatsRecorder, "log_metrics")
@patch.object(MasterNodeStatsRecorder, "_stop_request_stats_logger")
@patch.object(MasterNodeStatsRecorder, "_log_total_stats")
@patch.object(MasterNodeStatsRecorder, "_log_entry_stats")
@patch.object(MasterNodeStatsRecorder, "_log_error_stats")
def test_on_test_stop_calls_helpers_and_logs(
    mock_errors,
    mock_entries,
    mock_total,
    mock_stop,
    mock_log,
    mock_sleep,
    mock_env,
):
    """Test that on_test_stop calls all helper methods and logs the stop event."""
    recorder = MasterNodeStatsRecorder(mock_env)
    recorder.on_test_stop()

    mock_stop.assert_called_once()
    mock_total.assert_called_once_with(final=True)
    mock_entries.assert_called_once()
    mock_errors.assert_called_once()
    mock_sleep.assert_called_once_with(0.1)
    mock_log.assert_called_once_with(
        metric=EventsEnum.TEST_STOP_EVENT.value,
        text="test-plan finished. Stopping the tests.",
    )


@patch.object(MasterNodeStatsRecorder, "log_metrics")
def test_on_spawning_complete_logs_event(mock_log, mock_env):
    """Test that on_spawning_complete logs the expected event with user count."""
    recorder = MasterNodeStatsRecorder(mock_env)
    recorder.on_spawning_complete(user_count=10)

    mock_log.assert_called_once_with(
        metric=EventsEnum.SPAWN_COMPLETE_EVENT.value,
        user_count=10,
        text="test-plan ramp-up complete, 10 users spawned",
    )


def test_get_stats_converts_percentiles(mock_env):
    """Test that _get_stats converts Locust percentile keys correctly."""
    recorder = MasterNodeStatsRecorder(mock_env)
    st = MagicMock()
    st.to_dict.return_value = {
        "response_time_percentile_0.95": 100,
        "response_time_percentile_0.99": 200,
        "other": "val",
    }

    result = recorder._get_stats(st)
    assert result["percentile_95"] == 100
    assert result["percentile_99"] == 200
    assert result["other"] == "val"


@patch.object(MasterNodeStatsRecorder, "log_metrics")
def test_log_total_stats_final_and_current(mock_log, mock_env):
    """Test that _log_total_stats logs both current and final metrics."""
    recorder = MasterNodeStatsRecorder(mock_env)
    mock_env.runner.user_count = 5

    recorder._log_total_stats(final=False)
    recorder._log_total_stats(final=True)
    assert mock_log.call_count == 2


@patch.object(MasterNodeStatsRecorder, "log_metrics")
def test_log_entry_and_error_stats(mock_log, mock_env):
    """Test that _log_entry_stats and _log_error_stats invoke log_metrics."""
    recorder = MasterNodeStatsRecorder(mock_env)
    mock_env.stats.entries = {("/api", "GET"): MagicMock()}
    mock_env.stats.errors = {"err": MagicMock()}

    recorder._log_entry_stats()
    recorder._log_error_stats()
    assert mock_log.call_count == 2


def test_stop_request_stats_logger_kills_greenlet(mock_env):
    """Test that _stop_request_stats_logger kills the greenlet if it exists."""
    recorder = MasterNodeStatsRecorder(mock_env)
    greenlet = MagicMock()
    recorder._request_stats_logger = greenlet

    recorder._stop_request_stats_logger()
    greenlet.kill.assert_called_once()
    assert recorder._request_stats_logger is None


@patch.object(MasterNodeStatsRecorder, "_log_total_stats")
@patch("gevent.sleep", return_value=None)
def test_log_request_stats_loops_until_runner_none(mock_total, mock_sleep, mock_env):
    """Test that _log_request_stats loops until the environment runner is None."""
    recorder = MasterNodeStatsRecorder(mock_env)
    call_count = [0]

    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] > 2:
            mock_env.runner = None

    mock_total.side_effect = side_effect
    recorder._log_request_stats()
    assert call_count[0] > 2
