"""
Core handler abstractions for Locust Telemetry integration.

This module defines abstract base classes (ABCs) that serve as contracts for
handling Locust events and recording telemetry. These abstractions separate
event handling (e.g., test lifecycle, requests, system metrics) from the
concrete output mechanism (e.g., JSON logs, OpenTelemetry exporters).

Responsibilities
----------------
- Provide a consistent interface for telemetry event and metric recording.
- Enable flexible output strategies via the `OutputHandlerBase`.
- Minimize recorder boilerplate by delegating event handling to specialized
  handler classes.

Design Notes
------------
- These base classes should live under ``locust_telemetry/core`` as they
  define the foundational contracts of the telemetry framework.
- Shared helpers (e.g., metric collectors, enums) belong in
  ``locust_telemetry/common``.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from locust.env import Environment
from locust.runners import MasterRunner

from locust_telemetry.core.events import TelemetryEventsEnum, TelemetryMetricsEnum


class BaseOutputHandler(ABC):
    """
    Abstract base class for telemetry output handlers.

    Implementations define how telemetry events and metrics are emitted, such as:
    - Writing structured JSON logs
    - Exporting OpenTelemetry signals
    - Integrating with custom monitoring backends

    Each handler receives the Locust ``Environment`` for context.

    Responsibilities
    ----------------
    - Serialize and dispatch telemetry events.
    - Record metrics with associated attributes.
    - Provide run-level context (e.g., run_id, testplan, source).
    """

    def __init__(self, env: Environment):
        self.env = env

    def get_run_context(self) -> Dict:
        """
        Retrieve common run-level context for telemetry records.

        Returns
        -------
        dict
            Dictionary with run metadata including ``run_id``, ``testplan``,
            and runner identity (master or worker).
        """
        return {
            "run_id": self.env.telemetry_meta.run_id,
            "testplan": self.env.parsed_options.testplan,
            "source": self.env.runner.__class__.__name__,
            "source_id": (
                "master"
                if isinstance(self.env.runner, MasterRunner)
                else f"worker-{self.env.runner.worker_index}"
            ),
        }

    @abstractmethod
    def record_event(
        self, tl_type: TelemetryEventsEnum, *args: Any, **kwargs: Any
    ) -> None:
        """
        Record a telemetry event.

        Parameters
        ----------
        tl_type : TelemetryEvent
            Enum value representing the telemetry event type.
        args : tuple
            Event-specific arguments.
        kwargs : dict
            Additional event metadata.
        """
        raise NotImplementedError

    @abstractmethod
    def record_metrics(
        self, tl_type: TelemetryMetricsEnum, *args: Any, **kwargs: Any
    ) -> None:
        """
        Record a telemetry metric.

        Parameters
        ----------
        tl_type : TelemetryMetric
            Enum value representing the telemetry metric type.
        args : tuple
            Metric-specific arguments (e.g., value).
        kwargs : dict
            Additional metric attributes.
        """
        raise NotImplementedError


class BaseLifecycleHandler:
    """
    Abstract base class for handling Locust test lifecycle events.

    Responds to key lifecycle transitions such as ``test_start``, ``test_stop``,
    ``spawning_complete``, and ``cpu_warning``. Implementations typically
    forward these events to a telemetry output handler.

    Responsibilities
    ----------------
    - Translate Locust lifecycle events into telemetry signals.
    - Invoke ``OutputHandlerBase.record_event`` with appropriate metadata.
    """

    def __init__(self, output: BaseOutputHandler, env: Environment):
        self.output = output
        self.env = env

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """Invoked when a Locust test starts."""
        self.output.record_event(
            TelemetryEventsEnum.TEST_START,
            *args,
            **kwargs,
        )

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """Invoked when a Locust test stops."""
        self.output.record_event(
            TelemetryEventsEnum.TEST_STOP,
            *args,
            **kwargs,
        )

    def on_spawning_complete(self, *args: Any, **kwargs: Any) -> None:
        """Invoked when all users have been spawned."""
        self.output.record_event(TelemetryEventsEnum.SPAWNING_COMPLETE, *args, **kwargs)

    def on_cpu_warning(self, *args: Any, **kwargs: Any) -> None:
        """Invoked when Locust raises a CPU usage warning."""
        self.output.record_event(TelemetryEventsEnum.CPU_WARNING, *args, **kwargs)


class BaseRequestHandler(ABC):
    """
    Abstract base class for handling Locust request events.

    Transforms request/response events into telemetry signals, such as request
    durations, status codes, or error rates.

    Responsibilities
    ----------------
    - Handle request events emitted by Locust.
    - Forward request metadata to the telemetry output handler.
    """

    def __init__(self, output: BaseOutputHandler, env: Environment):
        self.output = output
        self.env = env

    @abstractmethod
    def start(self) -> None:
        """Start requests metrics collection (push loop or callback registration)."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop requests metrics collection and clean up resources"""
        pass

    @abstractmethod
    def on_request(self, *args: Any, **kwargs: Any) -> None:
        """
        Invoked for each Locust request event.

        Parameters
        ----------
        args : tuple
            Request-specific arguments (e.g., type, name, response time).
        kwargs : dict
            Additional request metadata.
        """
        raise NotImplementedError


class BaseSystemMetricsHandler(ABC):
    """
    Abstract base class for system metrics collection.

    Controls the lifecycle of metrics recording. Implementations may:
    - Start a background loop to periodically push metrics (e.g., JSON logging).
    - Register pull-based callbacks (e.g., OpenTelemetry observables).

    Responsibilities
    ----------------
    - Manage start/stop of system metrics collection.
    - Emit system-level metrics (e.g., CPU, memory, network).
    """

    def __init__(self, output: BaseOutputHandler, env: Environment):
        self.output = output
        self.env = env

    @abstractmethod
    def start(self) -> None:
        """Start system metrics collection (push loop or callback registration)."""
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """Stop system metrics collection and clean up resources."""
        raise NotImplementedError
