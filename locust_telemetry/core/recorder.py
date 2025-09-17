import os
import socket
from abc import ABC
from typing import Any, Optional, Type

from locust.env import Environment

from locust_telemetry.core.handlers import (
    BaseLifecycleHandler,
    BaseOutputHandler,
    BaseRequestHandler,
    BaseSystemMetricsHandler,
)


class BaseTelemetryRecorder(ABC):
    """
    Abstract base class for telemetry recorders.

    Responsibilities
    ----------------
    - Store the Locust environment and telemetry handlers.
    - Provide helper methods for concrete recorders.
    - Allow subclasses to register event listeners as needed.
    """

    def __init__(
        self,
        env: Environment,
        output_handler_cls: Type[BaseOutputHandler],
        lifecycle_handler_cls: Type[BaseLifecycleHandler],
        system_handler_cls: Type[BaseSystemMetricsHandler],
        requests_handler_cls: Type[BaseRequestHandler],
    ) -> None:
        self.env: Environment = env
        self._username: str = os.getenv("USER", "unknown")
        self._hostname: str = socket.gethostname()
        self._pid: int = os.getpid()

        # Initialize handlers
        self.output = output_handler_cls(env)
        self.lifecycle = lifecycle_handler_cls(self.output, env)
        self.system = system_handler_cls(self.output, env)
        self.requests = requests_handler_cls(self.output, env)

    def on_cpu_warning(
        self,
        environment: Environment,
        cpu_usage: float,
        message: Optional[str] = None,
        timestamp: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """
        Handle a CPU usage warning raised by Locust.

        Forwards the warning to the lifecycle handler with telemetry metadata.

        Parameters
        ----------
        environment : Environment
            The Locust environment instance.
        cpu_usage : float
            Current CPU usage percentage.
        message : Optional[str], optional
            Additional message describing the warning.
        timestamp : Optional[float], optional
            UNIX timestamp when the warning occurred.
        **kwargs : Any
            Additional keyword arguments from the Locust event.
        """
        self.lifecycle.on_cpu_warning(value=cpu_usage, unit="percent")

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        Base handler for test start event.

        Registers CPU warning listener. Subclasses can extend
        this method to start other handlers.
        """
        self.env.events.cpu_warning.add_listener(self.on_cpu_warning)

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Base handler for test stop event.

        Removes CPU warning listener. Subclasses can extend
        this method to stop other handlers.
        """
        self.env.events.cpu_warning.remove_listener(self.on_cpu_warning)


class MasterTelemetryRecorder(BaseTelemetryRecorder):
    """
    Telemetry recorder for the Locust master node.

    Registers master-specific event listeners and coordinates telemetry
    collection across system, lifecycle, and request metrics.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Register master-only event listeners
        self.env.events.test_start.add_listener(self.on_test_start)
        self.env.events.test_stop.add_listener(self.on_test_stop)
        self.env.events.spawning_complete.add_listener(self.on_spawning_complete)

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle the `test_start` event.

        Starts lifecycle recording, request metrics collection, and
        system metrics collection.
        """
        super().on_test_start(*args, **kwargs)
        self.lifecycle.on_test_start(*args, **kwargs)
        self.requests.start()
        self.system.start()

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle the `test_stop` event.

        Stops request metrics and system metrics collection, and forwards
        the event to the lifecycle handler.
        """
        super().on_test_stop(*args, **kwargs)
        self.lifecycle.on_test_stop(*args, **kwargs)
        self.requests.stop()
        self.system.stop()

    def on_spawning_complete(self, user_count: int) -> None:
        """
        Handle the `spawning_complete` event.

        Parameters
        ----------
        user_count : int
            Number of users that have been spawned.
        """
        self.lifecycle.on_spawning_complete(user_count=user_count)


class WorkerTelemetryRecorder(BaseTelemetryRecorder):
    """
    Telemetry recorder for the Locust worker node.

    Focuses on system metrics and CPU warnings, delegating lifecycle
    event logging to the master.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Register worker event listeners
        self.env.events.test_start.add_listener(self.on_test_start)
        self.env.events.test_stop.add_listener(self.on_test_stop)

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle the `test_start` event.

        Starts system metrics collection and registers a CPU warning listener.

        Note
        ----
        Lifecycle events are handled by the master, so no call to
        `self.lifecycle.on_test_start`.
        """
        self.system.start()

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle the `test_stop` event.

        Stops system metrics collection and unregisters the CPU warning listener.

        Note
        ----
        Lifecycle events are handled by the master, so no call to
        `self.lifecycle.on_test_stop`.
        """
        self.system.stop()
