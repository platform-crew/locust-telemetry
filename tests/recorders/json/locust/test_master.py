"""
Tests for MasterLocustJsonTelemetryRecorder.

These tests verify:
- Proper initialization and event listener registration
- Event handlers (test_start, test_stop, spawning_complete)
- Background request stats logging
- Helper methods for stats formatting and logging
"""

from unittest.mock import ANY, MagicMock, patch

import gevent
import pytest
from locust.env import Environment

from locust_telemetry.recorders.json.locust.constants import (
    LocustTestEvent,
    RequestMetric,
)
from locust_telemetry.recorders.json.locust.master import (
    MasterLocustJsonTelemetryRecorder,
)


@pytest.fixture
def recorder(mock_env: Environment) -> MasterLocustJsonTelemetryRecorder:
    """Return an initialized MasterLocustJsonTelemetryRecorder."""
    return MasterLocustJsonTelemetryRecorder(env=mock_env)


def test_initialization_registers_event_listeners(mock_env: Environment) -> None:
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


def test_on_test_start_starts_greenlet_and_logs_telemetry(
    recorder: MasterLocustJsonTelemetryRecorder,
) -> None:
    """Test that on_test_start spawns the background logger and emits telemetry."""
    with (
        patch.object(recorder, "log_telemetry") as mock_log,
        patch("gevent.spawn") as mock_gevent_spawn,
    ):
        mock_greenlet = MagicMock()
        mock_gevent_spawn.return_value = mock_greenlet
        recorder.on_test_start()
        assert mock_gevent_spawn.call_count == 2
        mock_log.assert_called_once_with(
            telemetry=LocustTestEvent.START.value,
            num_clients=recorder.env.parsed_options.num_users,
            profile_name=recorder.env.parsed_options.profile,
            username=recorder._username,
        )


def test_on_test_stop_stops_logger_and_logs_final_stats(
    recorder: MasterLocustJsonTelemetryRecorder,
) -> None:
    """Test that on_test_stop stops greenlet, logs stats, and emits telemetry."""
    stats_logger_mock = MagicMock()
    recorder._request_stats_logger = stats_logger_mock
    with (
        patch.object(recorder, "_log_total_stats") as mock_total,
        patch.object(recorder, "_log_entry_stats") as mock_entry,
        patch.object(recorder, "_log_error_stats") as mock_error,
        patch.object(recorder, "log_telemetry") as mock_log,
    ):
        recorder.on_test_stop()
        stats_logger_mock.kill.assert_called_once()
        mock_total.assert_called_once_with(final=True)
        mock_entry.assert_called_once()
        mock_error.assert_called_once()
        mock_log.assert_called_once_with(
            telemetry=LocustTestEvent.STOP.value,
            endtime=ANY,
            text=f"{recorder.env.parsed_options.testplan} "
            f"finished. Stopping the tests.",
        )


def test_on_spawning_complete_logs_telemetry(
    recorder: MasterLocustJsonTelemetryRecorder,
) -> None:
    """Test that on_spawning_complete logs the correct telemetry."""
    with patch.object(recorder, "log_telemetry") as mock_log:
        recorder.on_spawning_complete(user_count=10)
        mock_log.assert_called_once_with(
            telemetry=LocustTestEvent.SPAWN_COMPLETE.value,
            user_count=10,
            text=(
                f"{recorder.env.parsed_options.testplan} "
                f"ramp-up complete, 10 users spawned"
            ),
        )


def test_get_stats_formats_percentiles(
    recorder: MasterLocustJsonTelemetryRecorder, mock_env: Environment
) -> None:
    """Ensure _get_stats correctly maps percentile keys."""
    # Mock the stats dict returned by .to_dict()
    mock_env.stats.total.to_dict.return_value = {
        "response_time_percentile_0.95": 150,
        "response_time_percentile_0.99": 200,
        "other_key": "value",
    }

    stats_dict = recorder._get_stats(mock_env.stats.total)
    assert stats_dict["percentile_95"] == 150
    assert stats_dict["percentile_99"] == 200
    # other keys are preserved
    assert stats_dict["other_key"] == "value"


def test_stop_request_stats_logger_kills_greenlet(
    recorder: MasterLocustJsonTelemetryRecorder,
) -> None:
    """Verify that _stop_request_stats_logger kills the greenlet if running."""
    mock_greenlet = MagicMock()
    recorder._request_stats_logger = mock_greenlet
    recorder._stop_request_stats_logger()
    mock_greenlet.kill.assert_called_once()
    assert recorder._request_stats_logger is None


def test_log_total_stats_calls_log_telemetry(
    recorder: MasterLocustJsonTelemetryRecorder,
) -> None:
    """Ensure _log_total_stats calls log_telemetry with the correct telemetry type."""
    with patch.object(recorder, "log_telemetry") as mock_log:
        recorder._log_total_stats(final=True)
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert kwargs["telemetry"] == RequestMetric.FINAL_STATS.value


def test_log_request_stats_handles_greenlet_exit(
    recorder: MasterLocustJsonTelemetryRecorder, mock_env: Environment
) -> None:
    """Verify _log_request_stats loops and stops cleanly on GreenletExit."""
    with (
        patch.object(recorder, "_log_total_stats") as mock_total,
        patch("gevent.sleep") as mock_sleep,
    ):
        # Raise GreenletExit inside _log_total_stats
        mock_total.side_effect = gevent.GreenletExit()
        # Should not raise outside because the method catches it
        recorder._log_request_stats()

        # Confirm _log_total_stats was called once before exiting
        mock_total.assert_called_once()
        # gevent.sleep is never reached due to immediate GreenletExit
        mock_sleep.assert_not_called()


def test_log_entry_stats_calls_log_telemetry_for_each_entry(
    recorder: MasterLocustJsonTelemetryRecorder, mock_env: Environment
) -> None:
    """Ensure _log_entry_stats logs telemetry for each endpoint entry."""
    # Setup mock entries
    mock_env.stats.entries = {
        ("/api/foo", "GET"): MagicMock(),
        ("/api/bar", "POST"): MagicMock(),
    }
    for stats in mock_env.stats.entries.values():
        stats.to_dict.return_value = {
            "response_time_percentile_0.95": 100,
            "response_time_percentile_0.99": 200,
        }

    with patch.object(recorder, "log_telemetry") as mock_log:
        recorder._log_entry_stats()
        # Should be called twice (one per entry)
        assert mock_log.call_count == len(mock_env.stats.entries)
        for call_args in mock_log.call_args_list:
            kwargs = call_args.kwargs
            assert kwargs["telemetry"] == RequestMetric.ENDPOINT_STATS.value
            assert "request_path" in kwargs
            assert kwargs["percentile_95"] == 100
            assert kwargs["percentile_99"] == 200


def test_log_error_stats_calls_log_telemetry_for_each_error(
    recorder: MasterLocustJsonTelemetryRecorder, mock_env: Environment
) -> None:
    """Ensure _log_error_stats logs telemetry for each error entry."""
    # Setup mock errors
    mock_env.stats.errors = {
        "/api/foo": MagicMock(),
        "/api/bar": MagicMock(),
    }
    for err in mock_env.stats.errors.values():
        err.to_dict.return_value = {
            "response_time_percentile_0.95": 120,
            "response_time_percentile_0.99": 240,
        }

    with patch.object(recorder, "log_telemetry") as mock_log:
        recorder._log_error_stats()
        # Should be called once per error
        assert mock_log.call_count == len(mock_env.stats.errors)
        for call_args in mock_log.call_args_list:
            kwargs = call_args.kwargs
            assert kwargs["telemetry"] == RequestMetric.ENDPOINT_ERRORS.value
            assert kwargs["percentile_95"] == 120
            assert kwargs["percentile_99"] == 240


def test_log_request_stats_loops_and_calls_sleep(
    recorder: MasterLocustJsonTelemetryRecorder,
):
    """Ensure _log_request_stats loops and sleeps at the configured interval."""
    # Patch env.runner and parsed_options
    recorder.env.runner = MagicMock(user_count=5)
    recorder.env.stats.total.to_dict.return_value = {
        "response_time_percentile_0.95": 150,
        "response_time_percentile_0.99": 200,
    }
    recorder.env.parsed_options.locust_telemetry_recorder_interval = 0.1

    # Patch _log_total_stats to break after first iteration
    with (
        patch.object(recorder, "_log_total_stats") as mock_total,
        patch("gevent.sleep") as mock_sleep,
    ):
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count > 1:
                raise gevent.GreenletExit()

        mock_total.side_effect = side_effect

        recorder._log_request_stats()
        # Ensure _log_total_stats was called at least twice
        assert mock_total.call_count >= 2
        # gevent.sleep should have been called
        assert mock_sleep.call_count >= 1


def test_log_request_stats_returns_if_runner_none(
    recorder: MasterLocustJsonTelemetryRecorder,
):
    """Ensure _log_request_stats returns immediately if runner is None."""
    recorder.env.runner = None
    with (
        patch.object(recorder, "_log_total_stats") as mock_total,
        patch("gevent.sleep") as mock_sleep,
    ):
        recorder._log_request_stats()
        mock_total.assert_not_called()
        mock_sleep.assert_not_called()
