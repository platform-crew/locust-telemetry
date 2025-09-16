import logging
from typing import Any, ClassVar, Optional

from locust.env import Environment

from locust_telemetry.core.recorder import TelemetryBaseRecorder
from locust_telemetry.recorders.otel.metrics import OtelMetricsDefinition
from locust_telemetry.recorders.otel.mixins import LocustOtelCommonRecorderMixin

logger = logging.getLogger(__name__)


class MasterLocustOtelRecorder(LocustOtelCommonRecorderMixin, TelemetryBaseRecorder):
    """
    OpenTelemetry recorder for Locust master nodes.

    Integrates system and request-level telemetry collection, handling
    test lifecycle events and exporting metrics via OpenTelemetry.

    Inherits
    --------
    LocustOtelCommonRecorderMixin : Provides system metrics (CPU, memory, network)
    TelemetryBaseRecorder : Base recorder interface for Locust telemetry

    Attributes
    ----------
    name : ClassVar[str]
        Unique identifier for this recorder type.
    metrics : Optional[OtelMetricsDefinition]
        Container for all OpenTelemetry metrics instruments (gauges, histograms).
    """

    name: ClassVar[str] = "master_otel_recorder"

    def __init__(self, env: Environment) -> None:
        """
        Initialize the Master OpenTelemetry recorder.

        Sets up OpenTelemetry configuration, initializes metrics container,
        and registers event listeners for test lifecycle events.

        Parameters
        ----------
        env : Environment
            Locust environment instance providing access to test state
            and event hooks.
        """
        super().__init__(env)

        self.metrics: Optional[OtelMetricsDefinition] = None

        # Configure OpenTelemetry meter when environment initializes
        env.events.init.add_listener(self.configure_otel)

        # Register event listeners for test lifecycle
        env.events.test_start.add_listener(self.on_test_start)
        env.events.test_stop.add_listener(self.on_test_stop)
        env.events.spawning_complete.add_listener(self.on_spawning_complete)

    def on_test_start(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle the start of a Locust test.

        Invokes system metrics initialization, records a "test_start" event,
        and logs the start of OpenTelemetry metrics collection.

        Parameters
        ----------
        *args : Any
            Positional arguments from the event dispatcher.
        **kwargs : Any
            Keyword arguments from the event dispatcher.
        """
        logger.info("[otel] Initializing OpenTelemetry metrics collection")
        super().on_test_start(*args, **kwargs)

        # Record test start event
        self.metrics.events.test_event.record(
            self.now_ms, attributes=self.recorder_context(event="test_start")
        )

        logger.info(
            "[otel] Test initiated - OpenTelemetry metrics collection active",
            extra=self.recorder_context(),
        )

    def on_test_stop(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle the end of a Locust test.

        Stops system metrics collection, records a "test_stop" event,
        and logs completion of OpenTelemetry metrics export.

        Parameters
        ----------
        *args : Any
            Positional arguments from the event dispatcher.
        **kwargs : Any
            Keyword arguments from the event dispatcher.
        """
        super().on_test_stop(*args, **kwargs)

        # Record test stop event
        self.metrics.events.test_event.record(
            self.now_ms, attributes=self.recorder_context(event="test_stop")
        )

        logger.info(
            "[otel] Test completed - final metrics recorded and exported",
            extra=self.recorder_context(),
        )

    def on_spawning_complete(self, user_count: int) -> None:
        """
        Handle completion of user spawning.

        Records a "spawning_complete" event with the total number of active
        virtual users and logs this information.

        Parameters
        ----------
        user_count : int
            Total number of virtual users successfully spawned.
        """
        self.metrics.events.test_event.record(
            self.now_ms,
            attributes=self.recorder_context(
                event="spawning_complete", user_count=user_count
            ),
        )

        logger.info(
            f"[otel] User spawning completed - {user_count} virtual users active",
            extra=self.recorder_context(),
        )
