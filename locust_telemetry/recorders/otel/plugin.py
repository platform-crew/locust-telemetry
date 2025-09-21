import logging
from typing import Any, Dict

from locust.env import Environment

from locust_telemetry import config
from locust_telemetry.core.plugin import BaseTelemetryRecorderPlugin
from locust_telemetry.recorders.otel.exceptions import OtelConfigurationError
from locust_telemetry.recorders.otel.handlers import (
    OtelLifecycleHandler,
    OtelOutputHandler,
    OtelRequestHandler,
    OtelSystemMetricsHandler,
)
from locust_telemetry.recorders.otel.otel import configure_otel
from locust_telemetry.recorders.otel.recorder import (
    MasterLocustOtelRecorder,
    WorkerLocustOtelRecorder,
)

logger = logging.getLogger(__name__)


class LocustOtelRecorderPlugin(BaseTelemetryRecorderPlugin):
    """
    OpenTelemetry Recorder Plugin for Locust.

    This plugin integrates Locust with OpenTelemetry (OTel), enabling the export
    of metrics and lifecycle events to an OTLP endpoint. It provides recorder
    implementations for both master and worker nodes.

    Features
    --------
    - Registers CLI arguments for OTLP exporter configuration.
    - Instantiates master and worker OTel recorders.
    - Supports trace context injection into requests for downstream correlation.

    Notes
    -----
    - Master node uses :class:`MasterLocustOtelRecorder`.
    - Worker nodes use :class:`WorkerLocustOtelRecorder`.
    - Exporter configuration can be provided via CLI or environment variables.
    """

    #: Unique plugin identifier for the OpenTelemetry recorder
    RECORDER_PLUGIN_ID = config.TELEMETRY_OTEL_RECORDER_PLUGIN_ID

    def add_test_metadata(self) -> Dict[str, Any]:
        """
        Provide test-level metadata to attach to OTel metrics and traces.

        Returns
        -------
        Dict[str, Any]
            Key-value metadata pairs. Defaults to an empty dictionary.
        """
        return {}

    def add_cli_arguments(self, group: Any) -> None:
        """
        Register CLI arguments for configuring the OpenTelemetry OTLP exporter.

        Parameters
        ----------
        group : argparse._ArgumentGroup
            CLI argument group for plugin-specific arguments.

        Notes
        -----
        Arguments support environment variable overrides.
        """
        group.add_argument(
            "--lt-otel-exporter-otlp-endpoint",
            type=str,
            help=(
                "OTLP exporter endpoint for Locust metrics "
                "(e.g., http://otel-collector:4317)"
            ),
            env_var="LOCUST_OTEL_EXPORTER_OTLP_ENDPOINT",
            default="",
        )
        group.add_argument(
            "--lt-otel-exporter-otlp-insecure",
            type=bool,
            help="Use insecure (non-TLS) connection to the OTLP endpoint.",
            env_var="LOCUST_OTEL_EXPORTER_OTLP_INSECURE",
            default=False,
        )
        group.add_argument(
            "--lt-otel-trace-injection-by-header",
            type=bool,
            help=(
                "Enable trace propagation via HTTP headers. "
                "Use when no OTLP exporter is available, so trace context is "
                "still injected into Locust requests for correlation."
            ),
            env_var="LOCUST_OTEL_TRACE_INJECTION_BY_HEADER",
            default=True,
        )

    def load_master_telemetry_recorders(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Initialize and load the OTel recorder for the master node.

        Parameters
        ----------
        environment : Environment
            Locust runtime environment.
        **kwargs : Any
            Additional plugin arguments.
        """
        MasterLocustOtelRecorder(
            env=environment,
            output_handler_cls=OtelOutputHandler,
            lifecycle_handler_cls=OtelLifecycleHandler,
            system_handler_cls=OtelSystemMetricsHandler,
            requests_handler_cls=OtelRequestHandler,
        )
        logger.debug("[otel] Master OTel recorder initialized.")

    def load_worker_telemetry_recorders(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Initialize and load the OTel recorder for worker nodes.

        Parameters
        ----------
        environment : Environment
            Locust runtime environment.
        **kwargs : Any
            Additional plugin arguments.
        """
        WorkerLocustOtelRecorder(
            env=environment,
            output_handler_cls=OtelOutputHandler,
            lifecycle_handler_cls=OtelLifecycleHandler,
            system_handler_cls=OtelSystemMetricsHandler,
            requests_handler_cls=OtelRequestHandler,
        )
        logger.debug("[otel] Worker OTel recorder initialized.")

    def load(self, environment: Environment, **kwargs: Any) -> None:
        """
        Configure OTel and load the plugin into Locust.

        Parameters
        ----------
        environment : Environment
            Locust runtime environment.
        **kwargs : Any
            Additional plugin arguments.
        """
        try:
            configure_otel(environment)
            logger.info("[otel] OpenTelemetry configuration loaded successfully.")
        except Exception as e:
            raise OtelConfigurationError(
                "[otel] Something went wrong while configuring otel"
            ) from e
        super().load(environment, **kwargs)
