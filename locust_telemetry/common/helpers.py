from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional, Union

import psutil
from locust.env import Environment
from locust.runners import MasterRunner
from opentelemetry.metrics import (
    Counter,
    Histogram,
    Meter,
    ObservableCounter,
    ObservableGauge,
    ObservableUpDownCounter,
)

logger = logging.getLogger(__name__)


InstrumentType = Union[
    Counter, Histogram, ObservableGauge, ObservableCounter, ObservableUpDownCounter
]


@dataclass(frozen=True)
class InstrumentSpec:
    """
    Specification for creating an OpenTelemetry metric instrument.
    """

    metric: "TelemetryEventsEnum | TelemetryMetricsEnum"  # noqa: F821
    unit: str
    factory: Callable
    callbacks: Optional[List[Callable]] = None


def warmup_psutil(process: psutil.Process) -> None:
    """
    Initialize psutil process metrics to ensure accurate first readings.

    Many psutil methods, such as `cpu_percent()`, require a prior call to
    establish a baseline before returning meaningful values. This function
    calls the necessary methods to "warm up" the process metrics.

    Parameters
    ----------
    process : psutil.Process
        The process object for which to initialize CPU and memory statistics.

    Returns
    -------
    None
    """
    process.cpu_percent()
    process.memory_info()


def convert_bytes_to_mib(value: float) -> float:
    """
    Convert a value from bytes to mebibytes (MiB).

    Parameters
    ----------
    value : float
        The value in bytes.

    Returns
    -------
    float
        The equivalent value in mebibytes (1 MiB = 1024 * 1024 bytes).
    """
    return value / (1024 * 1024)


def get_utc_time_with_buffer(seconds_buffer: int) -> str:
    """
    Compute a UTC timestamp string with a buffer added, formatted in ISO 8601.

    Parameters
    ----------
    seconds_buffer : int
        Number of seconds to add to the current UTC time.

    Returns
    -------
    str
        ISO 8601 formatted UTC timestamp with 'Z' suffix,
        e.g., "2025-09-16T12:34:56.789Z".
    """
    value = datetime.now(timezone.utc) + timedelta(seconds=seconds_buffer)
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def add_percentiles(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add friendly percentile keys to a Locust stats dictionary.

    Converts Locust percentile keys to simpler names:
    - "response_time_percentile_0.95" -> "percentile_95"
    - "response_time_percentile_0.99" -> "percentile_99"

    Caution: This mutates the original dict. copy is intentionally not used because
    it's not necessary

    Parameters
    ----------
    stats : Dict[str, Any]
        Original Locust stats dictionary.

    Returns
    -------
    Dict[str, Any]
        Updated stats dictionary with `percentile_95` and `percentile_99` keys.
    """
    stats["percentile_95"] = stats.pop("response_time_percentile_0.95", "")
    stats["percentile_99"] = stats.pop("response_time_percentile_0.99", "")
    return stats


def create_otel_histogram(
    meter: Meter, name: str, description: str, unit: str = "ms", **kwargs
) -> Histogram:
    """
    Create an OpenTelemetry histogram for recording distributions of values.

    Parameters
    ----------
    meter : Meter
        OpenTelemetry Meter used to create the histogram.
    name : str
        Name of the metric.
    description : str
        Human-readable description of the metric.
    unit : str, optional
        Unit of measurement (default is "ms").

    Returns
    -------
    Histogram
        Configured histogram instrument.
    """
    return meter.create_histogram(name=name, description=description, unit=unit)


def create_otel_observable_gauge(
    meter: Meter,
    name: str,
    description: str,
    unit: str = "1",
    callbacks: Optional[List[Callable]] = None,
    **kwargs,
) -> ObservableGauge:
    """
    Create an OpenTelemetry Observable Gauge.

    Observable gauges capture instantaneous values, which are updated via
    callback functions.

    Parameters
    ----------
    meter : Meter
        OpenTelemetry Meter used to create the gauge.
    name : str
        Name of the metric.
    description : str
        Human-readable description of the metric.
    unit : str, optional
        Unit of measurement (default is dimensionless "1").
    callbacks : list[Callable], optional
        List of callback functions to provide gauge values.

    Returns
    -------
    Any
        Configured Observable Gauge instrument.
    """
    return meter.create_observable_gauge(
        name=name,
        description=description,
        unit=unit,
        callbacks=callbacks or [],
    )


def create_otel_counter(
    meter: Meter, name: str, description: str, unit: str = "1", **kwargs
) -> Counter:
    """
    Create an OpenTelemetry Counter instrument.

    A Counter is a cumulative metric that can only increase.
    Suitable for counting events (e.g., test start/stop events).

    Parameters
    ----------
    meter : Meter
        OpenTelemetry Meter used to create the counter.
    name : str
        Name of the metric.
    description : str
        Human-readable description of the metric.
    unit : str, optional
        Unit of measurement (default is dimensionless "1").

    Returns
    -------
    Counter
        Configured Counter instrument.
    """
    return meter.create_counter(name=name, description=description, unit=unit)


def get_source_id(env: Environment) -> str:
    """
    Get source if of the current runner. If its master then it returns as 'master'
    and for workers - it will return as 'worker-<index>'

    Parameters
    ----------
    env : Environment
        Locust environment

    Returns
    -------
    str
        If its master then it returns as 'master' and for workers -
        it will return as 'worker-<index>'
    """
    return (
        "master"
        if isinstance(env.runner, MasterRunner)
        else f"worker-{env.runner.worker_index}"
    )
