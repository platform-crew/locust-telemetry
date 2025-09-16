import logging
from functools import wraps
from typing import Callable

import psutil
from opentelemetry.metrics import Observation

from locust_telemetry.config import LOCUST_RUNNING_STATES
from locust_telemetry.core.recorder import TelemetryBaseRecorder

logger = logging.getLogger(__name__)

process = psutil.Process()


def callback_with_recorder(recorder: TelemetryBaseRecorder, func: Callable):
    """
    Wrap a callback function with a recorder instance and conditional execution.

    Ensures the callback only records metrics while the Locust test is running.

    Parameters
    ----------
    recorder : TelemetryBaseRecorder
        The recorder instance providing access to Locust environment and
        metrics context.
    func : Callable
        The original callback function accepting a recorder and returning Observations.

    Returns
    -------
    Callable
        Wrapped callback function suitable for OpenTelemetry observable gauges.
    """

    @wraps(func)
    def wrapper(options=None):
        # Only record metrics during the active testing window
        if recorder.env.runner.state not in LOCUST_RUNNING_STATES:
            return []
        return func(recorder)

    return wrapper


def user_count_callback(recorder: TelemetryBaseRecorder):
    """
    Observable callback for current active user count.

    Parameters
    ----------
    recorder : TelemetryBaseRecorder
        Recorder providing access to Locust environment and stats.

    Returns
    -------
    list[Observation]
        OpenTelemetry Observation containing user count and associated attributes.
    """
    logger.info("[otel] Collecting user count")
    stats = recorder.env.stats.total
    return [Observation(stats.user_count, recorder.recorder_context())]


def requests_count_callback(recorder: TelemetryBaseRecorder):
    """
    Observable callback for total number of requests executed.

    Returns
    -------
    list[Observation]
        OpenTelemetry Observation containing the cumulative request count.
    """
    logger.info("[otel] Collecting request count")
    stats = recorder.env.stats.total
    return [Observation(stats.num_requests, recorder.recorder_context())]


def failures_count_callback(recorder: TelemetryBaseRecorder):
    """
    Observable callback for total number of failed requests.

    Returns
    -------
    list[Observation]
        OpenTelemetry Observation containing the cumulative failure count.
    """
    logger.info("[otel] Collecting failure count")
    stats = recorder.env.stats.total
    return [Observation(stats.num_failures, recorder.recorder_context())]


def requests_per_second_callback(recorder: TelemetryBaseRecorder):
    """
    Observable callback for requests per second (RPS).

    Returns
    -------
    list[Observation]
        OpenTelemetry Observation containing the current RPS.
    """
    logger.info("[otel] Collecting RPS")
    stats = recorder.env.stats.total
    return [Observation(stats.num_reqs_per_sec, recorder.recorder_context())]


def failures_per_second_callback(recorder: TelemetryBaseRecorder):
    """
    Observable callback for failures per second (FPS).

    Returns
    -------
    list[Observation]
        OpenTelemetry Observation containing the current FPS.
    """
    logger.info("[otel] Collecting FPS")
    stats = recorder.env.stats.total
    return [Observation(stats.num_fail_per_sec, recorder.recorder_context())]


def cpu_usage_callback(recorder: TelemetryBaseRecorder):
    """
    Observable callback for system CPU usage.

    Returns
    -------
    list[Observation]
        OpenTelemetry Observation containing current CPU utilization percentage.
    """
    logger.info("[otel] Collecting CPU usage")
    return [Observation(process.cpu_percent(), recorder.recorder_context())]


def memory_usage_callback(recorder: TelemetryBaseRecorder):
    """
    Observable callback for process memory usage.

    Returns
    -------
    list[Observation]
        OpenTelemetry Observation containing current memory usage in MiB.
    """
    logger.info("[otel] Collecting Memory usage")
    memory_mib = process.memory_info().rss / (1024 * 1024)
    return [Observation(memory_mib, recorder.recorder_context())]


def network_usage_callback(recorder: TelemetryBaseRecorder):
    """
    Observable callback for network I/O counters.

    Returns
    -------
    list[Observation]
        Two OpenTelemetry Observations: bytes sent and bytes received,
        each with associated direction attributes.
    """
    logger.info("[otel] Collecting Network usage")
    current_io = psutil.net_io_counters()
    return [
        Observation(
            current_io.bytes_sent, {**recorder.recorder_context(), "direction": "sent"}
        ),
        Observation(
            current_io.bytes_recv, {**recorder.recorder_context(), "direction": "rec"}
        ),
    ]
