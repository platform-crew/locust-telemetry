import re
from datetime import datetime, timedelta, timezone
from unittest.mock import ANY, MagicMock

import psutil
import pytest
from freezegun import freeze_time

from locust_telemetry.common import helpers as h

ISO8601_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")


def test_warmup_calls_expected_methods():
    """warmup_psutil should call cpu_percent and memory_info exactly once."""
    fake_process = MagicMock(spec=psutil.Process)
    h.warmup_psutil(fake_process)

    fake_process.cpu_percent.assert_called_once_with()
    fake_process.memory_info.assert_called_once_with()


def test_warmup_with_real_process_does_not_raise():
    """warmup_psutil should not raise errors with a real psutil.Process."""
    process = psutil.Process()
    h.warmup_psutil(process)


def test_get_utc_time_format_is_iso8601():
    """Returned timestamp must match ISO 8601 with millisecond precision."""
    result = h.get_utc_time_with_buffer(0)
    assert ISO8601_REGEX.match(result), f"Unexpected format: {result}"


def test_get_utc_time_suffix_is_zulu():
    """Returned timestamp must end with 'Z' to denote UTC."""
    result = h.get_utc_time_with_buffer(0)
    assert result.endswith("Z")


@freeze_time("2025-09-30T12:00:00.123456Z")
def test_get_utc_time_buffer_applied_correctly():
    """Frozen time: adding buffer should yield expected deterministic result."""
    result = h.get_utc_time_with_buffer(5)
    expected = (
        (datetime.now(timezone.utc) + timedelta(seconds=5))
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )

    assert result == expected


@pytest.mark.parametrize("buffer", [-60, 0, 60, 3600])
def test_get_utc_time_various_buffers(buffer):
    """Adding different second buffers should produce correct timestamps."""
    result = h.get_utc_time_with_buffer(buffer)
    parsed = datetime.fromisoformat(result.replace("Z", "+00:00"))
    expected = datetime.now(timezone.utc) + timedelta(seconds=buffer)

    delta = abs((parsed - expected).total_seconds())
    assert delta < 1, f"Drift too large: {delta} seconds"


def test_add_percentiles_transforms_keys():
    """Original percentile keys should be renamed to friendly aliases."""
    stats = {
        "response_time_percentile_0.95": 123,
        "response_time_percentile_0.99": 456,
        "other_key": "value",
    }
    result = h.add_percentiles(stats)

    assert result["percentile_95"] == 123
    assert result["percentile_99"] == 456
    assert "response_time_percentile_0.95" not in result
    assert "response_time_percentile_0.99" not in result
    assert result["other_key"] == "value"


def test_add_percentiles_missing_keys_defaults():
    """Missing percentile keys should default to empty string."""
    stats = {"some_key": 42}
    result = h.add_percentiles(stats)

    assert result["percentile_95"] == ""
    assert result["percentile_99"] == ""
    assert result["some_key"] == 42


def test_add_percentiles_mutates_original():
    """Function should mutate original dictionary in place."""
    stats = {"response_time_percentile_0.95": 1}
    _ = h.add_percentiles(stats)

    assert "percentile_95" in stats
    assert "response_time_percentile_0.95" not in stats


def test_add_percentiles_overwrites_existing_keys():
    """New values should overwrite any pre-existing percentile keys."""
    stats = {
        "response_time_percentile_0.95": 5,
        "response_time_percentile_0.99": 10,
        "percentile_95": 999,
        "percentile_99": 888,
    }
    result = h.add_percentiles(stats)

    assert result["percentile_95"] == 5
    assert result["percentile_99"] == 10


def test_convert_bytes_zero():
    """Zero bytes should convert to 0 MiB."""
    assert h.convert_bytes_to_mib(0) == 0


def test_convert_bytes_one_mib():
    """Exact 1 MiB in bytes should convert to 1.0 MiB."""
    assert h.convert_bytes_to_mib(1024 * 1024) == 1.0


def test_convert_bytes_half_mib():
    """Half a MiB in bytes should convert to 0.5 MiB."""
    assert h.convert_bytes_to_mib(512 * 1024) == 0.5


def test_convert_bytes_large_value():
    """Multiple MiB in bytes should convert correctly."""
    assert h.convert_bytes_to_mib(10 * 1024 * 1024) == 10.0


def test_convert_bytes_fractional_value():
    """Small values should convert to fractional MiB."""
    assert h.convert_bytes_to_mib(1024) == pytest.approx(1 / 1024, rel=1e-9)


def test_convert_bytes_non_integer():
    """Non-integer byte values should convert properly."""
    result = h.convert_bytes_to_mib(1.5 * 1024 * 1024)
    assert result == 1.5


def test_convert_bytes_negative():
    """Negative byte values should convert to negative MiB."""
    assert h.convert_bytes_to_mib(-1024 * 1024) == -1.0


def test_get_source_id_master(mock_env_master):
    """When role=master, should return 'master'."""
    assert h.get_source_id(mock_env_master) == "master"


def test_get_source_id_worker(mock_env_worker):
    """When role=worker, should return worker-{index} (default index=2)."""
    assert h.get_source_id(mock_env_worker) == "worker-2"


def test_create_otel_histogram_uses_meter():
    """Wrapper should delegate to meter.create_histogram with defaults."""
    meter = MagicMock()
    histogram = MagicMock()
    meter.create_histogram.return_value = histogram

    result = h.create_otel_histogram(meter, "latency", "Request latency")

    meter.create_histogram.assert_called_once_with(
        name="latency", description="Request latency", unit="ms"
    )
    assert result is histogram


def test_create_otel_observable_gauge_with_callbacks():
    """Wrapper should pass through provided callbacks."""
    meter = MagicMock()
    gauge = MagicMock()
    meter.create_observable_gauge.return_value = gauge

    result = h.create_otel_observable_gauge(
        meter, "queue_depth", "Queue depth", callbacks=[lambda: 42]
    )

    meter.create_observable_gauge.assert_called_once_with(
        name="queue_depth", description="Queue depth", unit="1", callbacks=[ANY]
    )
    assert result is gauge


def test_create_otel_observable_gauge_defaults_callbacks_empty():
    """Wrapper should default callbacks to empty list if none provided."""
    meter = MagicMock()
    gauge = MagicMock()
    meter.create_observable_gauge.return_value = gauge

    result = h.create_otel_observable_gauge(meter, "cpu", "CPU usage")

    meter.create_observable_gauge.assert_called_once_with(
        name="cpu", description="CPU usage", unit="1", callbacks=[]
    )
    assert result is gauge


def test_create_otel_counter_uses_meter():
    """Wrapper should delegate to meter.create_counter with defaults."""
    meter = MagicMock()
    counter = MagicMock()
    meter.create_counter.return_value = counter

    result = h.create_otel_counter(meter, "requests", "Number of requests")

    meter.create_counter.assert_called_once_with(
        name="requests", description="Number of requests", unit="1"
    )
    assert result is counter
