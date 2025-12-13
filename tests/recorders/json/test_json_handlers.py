from unittest.mock import MagicMock, patch

import gevent

from locust_telemetry.core.events import TelemetryEventsEnum, TelemetryMetricsEnum
from locust_telemetry.recorders.json.constants import (
    REQUEST_STATS_TYPE_CURRENT,
    REQUEST_STATS_TYPE_FINAL,
)
from locust_telemetry.recorders.json.handlers import (
    JsonTelemetryLifecycleHandler,
    JsonTelemetryRequestHandler,
    JsonTelemetrySystemMetricsHandler,
)


def test_lifecycle_on_test_stop_patches_end_time(
    mock_env, json_output_handler, monkeypatch
):
    """
    JsonTelemetryLifecycleHandler.on_test_stop should call
    output.record_event with adjusted end_time.
    """
    handler = JsonTelemetryLifecycleHandler(output=json_output_handler, env=mock_env)

    # patch the helper that returns adjusted time
    monkeypatch.setattr(
        "locust_telemetry.recorders.json.handlers.h.get_utc_time_with_buffer",
        lambda seconds_buffer: 12345,
    )

    # Replace record_event with a spy so we can assert call and kwargs
    recorded = MagicMock()
    monkeypatch.setattr(json_output_handler, "record_event", recorded)

    handler.on_test_stop(reason="done")

    recorded.assert_called_once()
    args, kwargs = recorded.call_args
    # first arg should be TelemetryEventsEnum.TEST_STOP
    assert args[0] == TelemetryEventsEnum.TEST_STOP
    assert kwargs["end_time"] == 12345
    assert kwargs.get("reason") == "done"


@patch("locust_telemetry.recorders.json.handlers.h.warmup_psutil")
@patch("locust_telemetry.recorders.json.handlers.gevent.spawn")
def test_system_start_warmup_and_spawn(
    mock_spawn, mock_warmup, mock_env, json_output_handler
):
    """start() should warmup psutil and spawn a greenlet."""
    handler = JsonTelemetrySystemMetricsHandler(
        output=json_output_handler, env=mock_env
    )

    handler.start()

    mock_warmup.assert_called_once()
    mock_spawn.assert_called_once()


def test_system_stop_warns_if_not_started(mock_env, json_output_handler, caplog):
    """
    stop() should log a warning if start() wasn't called.
    """
    handler = JsonTelemetrySystemMetricsHandler(
        output=json_output_handler, env=mock_env
    )
    caplog.set_level("WARNING")

    handler._system_metrics_gevent = None
    handler.stop()

    assert any("Gevent loop never started" in r.getMessage() for r in caplog.records)


def test_system_stop_kills_greenlet_if_present(mock_env, json_output_handler):
    """
    stop() should kill an existing greenlet and clear the reference.
    """
    handler = JsonTelemetrySystemMetricsHandler(
        output=json_output_handler, env=mock_env
    )
    fake_g = MagicMock()
    handler._system_metrics_gevent = fake_g

    handler.stop()

    fake_g.kill.assert_called_once()
    assert handler._system_metrics_gevent is None


def test_system_gevent_loop_emits_metrics_once(
    mock_env, json_output_handler, monkeypatch
):
    """
    _gevent_loop should call output.record_metrics for CPU, MEMORY, NETWORK once,
    then exit when gevent.sleep raises GreenletExit.
    """
    handler = JsonTelemetrySystemMetricsHandler(
        output=json_output_handler, env=mock_env
    )

    # Patch psutil.net_io_counters and process methods/attributes
    fake_io = MagicMock(bytes_sent=1000, bytes_recv=2000)
    monkeypatch.setattr(
        "locust_telemetry.recorders.json.handlers.psutil.net_io_counters",
        lambda: fake_io,
    )

    # Patch the handler's _process to expose cpu_percent and memory_info
    class FakeProc:

        def cpu_percent(self):
            return 12.5

        def memory_info(self):
            m = MagicMock()
            m.rss = 1024 * 1024 * 10  # 10 MiB
            return m

    monkeypatch.setattr(handler, "_process", FakeProc())

    # convert bytes to MiB
    monkeypatch.setattr(
        "locust_telemetry.recorders.json.handlers.h.convert_bytes_to_mib",
        lambda b: b / (1024 * 1024),
    )

    # Make env parsed interval small and ensure gevent.sleep raises to break the loop
    mock_env.parsed_options.lt_stats_recorder_interval = 0.001
    monkeypatch.setattr(
        "locust_telemetry.recorders.json.handlers.gevent.sleep",
        lambda s: (_ for _ in ()).throw(gevent.GreenletExit()),
    )

    # Patch output.record_metrics so we can count calls
    rm = MagicMock()
    monkeypatch.setattr(json_output_handler, "record_metrics", rm)

    # Run loop (it will exit quickly due to patched sleep)
    handler._gevent_loop()

    # It should have recorded CPU, MEMORY, NETWORK sent & recv = 4 calls
    assert rm.call_count >= 4
    # verify first call type is TelemetryMetricsEnum.CPU
    first_args = rm.call_args_list[0][0]
    assert first_args[0] == TelemetryMetricsEnum.CPU


def test_request_start_only_on_master(
    mock_env_master, mock_env_worker, json_output_handler, monkeypatch
):
    """
    start() should spawn greenlet only when runner is not WorkerRunner.
    """
    handler_master = JsonTelemetryRequestHandler(
        output=json_output_handler, env=mock_env_master
    )
    handler_worker = JsonTelemetryRequestHandler(
        output=json_output_handler, env=mock_env_worker
    )

    with patch("locust_telemetry.recorders.json.handlers.gevent.spawn") as sp:
        handler_master.start()
        sp.assert_called_once()

    with patch("locust_telemetry.recorders.json.handlers.gevent.spawn") as sp2:
        handler_worker.start()
        sp2.assert_not_called()


def test_request_stop_warns_if_not_started(
    mock_env_master, json_output_handler, caplog
):
    """
    stop() should warn if not started (and runner is master).
    """
    handler = JsonTelemetryRequestHandler(
        output=json_output_handler, env=mock_env_master
    )
    caplog.set_level("WARNING")

    # ensure no greenlet
    handler._request_metrics_gevent = None
    handler.stop()

    assert any("Gevent loop never started" in r.getMessage() for r in caplog.records)


def test_request_stop_kills_and_flushes_final_stats(
    mock_env_master, json_output_handler, monkeypatch
):
    """
    stop() should kill the request greenlet and call _flush_stats which
    records final metrics.
    """
    handler = JsonTelemetryRequestHandler(
        output=json_output_handler, env=mock_env_master
    )
    fake_g = MagicMock()
    handler._request_metrics_gevent = fake_g

    # Patch output.record_metrics to spy
    rm = MagicMock()
    monkeypatch.setattr(json_output_handler, "record_metrics", rm)

    # prepare fake stats
    mock_env_master.runner.user_count = 7
    # total
    total = MagicMock()
    total.to_dict.return_value = {"total": 1}
    mock_env_master.stats.total = total
    # entries and errors
    entry = MagicMock()
    entry.to_dict.return_value = {"p": 1}
    mock_env_master.stats.entries = {"e1": entry}
    err = MagicMock()
    err.to_dict.return_value = {"p": 2}
    mock_env_master.stats.errors = {"e1": err}

    handler.stop()

    fake_g.kill.assert_called_once()
    # _flush_stats should have emitted at least one call for final totals
    assert rm.call_count >= 1

    # Verify one call used REQUEST_STATS_TYPE_FINAL
    found_final = any(
        call_args[1].get("stats_type") == REQUEST_STATS_TYPE_FINAL
        or (len(call_args[0]) > 1 and call_args[0][1] == REQUEST_STATS_TYPE_FINAL)
        for call_args in rm.call_args_list
    )
    assert found_final


def test_request_gevent_loop_emits_and_exits(
    mock_env_master, json_output_handler, monkeypatch
):
    """
    _gevent_loop should emit a current stats metric and exit gracefully on GreenletExit.
    """
    handler = JsonTelemetryRequestHandler(
        output=json_output_handler, env=mock_env_master
    )

    # Patch add_percentiles to return a flat dict
    monkeypatch.setattr(
        "locust_telemetry.recorders.json.handlers.h.add_percentiles", lambda d: d
    )

    # Prepare env stats total
    mock_env_master.stats.total.to_dict.return_value = {"count": 5}
    mock_env_master.runner.user_count = 3

    # Patch gevent.sleep to raise GreenletExit after one loop
    monkeypatch.setattr(
        "locust_telemetry.recorders.json.handlers.gevent.sleep",
        lambda s: (_ for _ in ()).throw(gevent.GreenletExit()),
    )

    # Spy on output.record_metrics
    rm = MagicMock()
    monkeypatch.setattr(json_output_handler, "record_metrics", rm)

    handler._gevent_loop()

    # Should have emitted at least one current stats metric
    assert rm.call_count >= 1
    # check that one of the calls used REQUEST_STATS_TYPE_CURRENT as stats_type
    assert any(
        (call_args[1].get("stats_type") == REQUEST_STATS_TYPE_CURRENT)
        or (len(call_args[0]) > 1 and call_args[0][1] == REQUEST_STATS_TYPE_CURRENT)
        for call_args in rm.call_args_list
    )
