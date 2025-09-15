"""
Unit tests for MasterLocustJsonTelemetryRecorder.

These tests verify:
- Proper initialization and event listener registration
- Event handlers: test_start, test_stop, spawning_complete
- Background request stats logging
- Helper methods for stats formatting and logging
- Edge cases like runner being None and GreenletExit handling
"""

from unittest.mock import MagicMock, patch

import gevent
from locust.env import Environment

from locust_telemetry.recorders.json.locust.constants import (
    LocustTestEvent,
    RequestMetric,
)
from locust_telemetry.recorders.json.locust.master import (
    MasterLocustJsonTelemetryRecorder,
)


def test_initialization_registers_event_listeners(mock_env: Environment):
    """Ensure event listeners are registered on initialization."""
    recorder = MasterLocustJsonTelemetryRecorder(env=mock_env)
    mock_env.events.test_start.add_listener.assert_called_once_with(
        recorder.on_test_start
    )
    mock_env.events.test_stop.add_listener.assert_called_once_with(
        recorder.on_test_stop
    )
    mock_env.events.spawning_complete.add_listener.assert_called_once_with(
        recorder.on_spawning_complete
    )


def test_on_test_start_starts_greenlet_and_logs_telemetry(master_json_recorder):
    """Test that on_test_start spawns the background logger and emits telemetry."""
    with (
        patch.object(master_json_recorder, "log_telemetry") as mock_log,
        patch("gevent.spawn") as mock_spawn,
    ):
        mock_greenlet = MagicMock()
        mock_spawn.return_value = mock_greenlet
        master_json_recorder.on_test_start()
        assert mock_spawn.call_count == 2  # One from mixin and another master recorder
        mock_log.assert_called_once_with(
            telemetry=LocustTestEvent.START.value,
            num_clients=master_json_recorder.env.parsed_options.num_users,
            profile_name=master_json_recorder.env.parsed_options.profile,
            username=master_json_recorder._username,
        )


def test_on_test_stop_stops_logger_and_logs_final_stats(master_json_recorder):
    """Test that on_test_stop stops greenlet, logs stats, and emits telemetry."""
    stats_logger_mock = MagicMock()
    master_json_recorder._request_stats_recorder = stats_logger_mock
    with patch.object(
        master_json_recorder, "log_request_stats"
    ) as mock_total, patch.object(
        master_json_recorder, "log_endpoint_success_stats"
    ) as mock_entry, patch.object(
        master_json_recorder, "log_endpoint_error_stats"
    ) as mock_error, patch.object(
        master_json_recorder, "log_telemetry"
    ) as mock_log:
        master_json_recorder.on_test_stop()
        stats_logger_mock.kill.assert_called_once()
        mock_total.assert_called_once_with(final=True)
        mock_entry.assert_called_once()
        mock_error.assert_called_once()
        mock_log.assert_called_once()
        assert mock_log.call_args.kwargs["telemetry"] == LocustTestEvent.STOP.value


def test_on_spawning_complete_logs_telemetry(master_json_recorder):
    """Test that on_spawning_complete logs the correct telemetry."""
    with patch.object(master_json_recorder, "log_telemetry") as mock_log:
        master_json_recorder.on_spawning_complete(user_count=10)
        mock_log.assert_called_once_with(
            telemetry=LocustTestEvent.SPAWN_COMPLETE.value,
            user_count=10,
            text=f"{master_json_recorder.env.parsed_options.testplan} ramp-up "
            f"complete, 10 users spawned",
        )


def test_stats_to_dict_maps_percentiles(mock_env, master_json_recorder):
    """Ensure stats_to_dict correctly maps percentile keys."""
    mock_env.stats.total.to_dict.return_value = {
        "response_time_percentile_0.95": 150,
        "response_time_percentile_0.99": 200,
        "other_key": "value",
    }
    stats_dict = master_json_recorder.stats_to_dict(
        master_json_recorder.env.stats.total
    )
    assert stats_dict["percentile_95"] == 150
    assert stats_dict["percentile_99"] == 200
    assert stats_dict["other_key"] == "value"


def test_stop_recording_request_stats_kills_greenlet(master_json_recorder):
    """Verify that stop_recording_request_stats kills the greenlet if running."""
    mock_greenlet = MagicMock()
    master_json_recorder._request_stats_recorder = mock_greenlet
    master_json_recorder.stop_recording_request_stats()
    mock_greenlet.kill.assert_called_once()
    assert master_json_recorder._request_stats_recorder is None


def test_start_recording_request_stats_handles_greenlet_exit(master_json_recorder):
    """Verify start_recording_request_stats stops cleanly on GreenletExit."""
    with (
        patch.object(master_json_recorder, "log_request_stats") as mock_total,
        patch("gevent.sleep") as mock_sleep,
    ):
        mock_total.side_effect = gevent.GreenletExit()
        master_json_recorder.start_recording_request_stats()
        mock_total.assert_called_once()
        mock_sleep.assert_not_called()


def test_start_recording_request_stats_loops_and_calls_sleep(master_json_recorder):
    """Ensure start_recording_request_stats loops and sleeps at configured interval."""
    with (
        patch.object(master_json_recorder, "log_request_stats") as mock_total,
        patch("gevent.sleep") as mock_sleep,
    ):
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count > 2:
                raise gevent.GreenletExit()

        mock_total.side_effect = side_effect
        master_json_recorder.start_recording_request_stats()
        assert mock_total.call_count == 3
        assert mock_sleep.call_count == 2


def test_log_request_stats_calls_log_telemetry(master_json_recorder):
    """Ensure log_request_stats calls log_telemetry with correct telemetry type."""
    with patch.object(master_json_recorder, "log_telemetry") as mock_log:
        master_json_recorder.log_request_stats(final=True)
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert kwargs["telemetry"] == RequestMetric.FINAL_STATS.value


def test_log_endpoint_success_stats_calls_log_telemetry(master_json_recorder):
    """Ensure log_endpoint_success_stats logs each endpoint entry."""
    master_json_recorder.env.stats.entries = {
        ("/api/foo", "GET"): MagicMock(
            to_dict=MagicMock(
                return_value={
                    "response_time_percentile_0.95": 100,
                    "response_time_percentile_0.99": 200,
                }
            )
        ),
        ("/api/bar", "POST"): MagicMock(
            to_dict=MagicMock(
                return_value={
                    "response_time_percentile_0.95": 150,
                    "response_time_percentile_0.99": 250,
                }
            )
        ),
    }
    with patch.object(master_json_recorder, "log_telemetry") as mock_log:
        master_json_recorder.log_endpoint_success_stats()
        assert mock_log.call_count == len(master_json_recorder.env.stats.entries)


def test_log_endpoint_error_stats_calls_log_telemetry(master_json_recorder):
    """Ensure log_endpoint_error_stats logs each error entry."""
    master_json_recorder.env.stats.errors = {
        "/api/foo": MagicMock(
            to_dict=MagicMock(
                return_value={
                    "response_time_percentile_0.95": 120,
                    "response_time_percentile_0.99": 240,
                }
            )
        ),
        "/api/bar": MagicMock(
            to_dict=MagicMock(
                return_value={
                    "response_time_percentile_0.95": 130,
                    "response_time_percentile_0.99": 260,
                }
            )
        ),
    }
    with patch.object(master_json_recorder, "log_telemetry") as mock_log:
        master_json_recorder.log_endpoint_error_stats()
        assert mock_log.call_count == len(master_json_recorder.env.stats.errors)
