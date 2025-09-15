import logging
from typing import Any, Dict

from locust.env import Environment

from locust_telemetry import config
from locust_telemetry.core.plugin import TelemetryRecorderPluginBase
from locust_telemetry.recorders.otel.master import MasterLocustOtelRecorder
from locust_telemetry.recorders.otel.worker import WorkerLocustOtelRecorder

logger = logging.getLogger(__name__)


class LocustOtelRecorderPlugin(TelemetryRecorderPluginBase):
    """
    OpenTelemetry Recorder Plugin for Locust.

    Responsibilities
    ----------------
    - Register CLI arguments for configuring OpenTelemetry exporters.
    - Instantiate appropriate OTel recorders for master and worker nodes.
    - Provide integration with Locust's telemetry plugin framework.

    Notes
    -----
    - On the master node, :class:`MasterLocustOtelRecorder` is loaded.
    - On worker nodes, :class:`WorkerLocustOtelRecorder` is loaded.
    - Exporter configuration is controlled via CLI arguments or environment variables.
    """

    #: Unique plugin identifier for OpenTelemetry recorder
    RECORDER_PLUGIN_ID = config.TELEMETRY_OTEL_RECORDER_PLUGIN_ID

    def add_test_metadata(self) -> Dict:
        """
        Add test-level metadata to be attached to metrics and traces.

        Returns
        -------
        Dict
            Key-value pairs of metadata. Empty by default.
        """
        return {}

    def add_cli_arguments(self, group: Any) -> None:
        """
        Define CLI arguments for configuring the OpenTelemetry exporter.

        Parameters
        ----------
        group : argparse._ArgumentGroup
            The CLI argument group where plugin-specific arguments will be added.

        Notes
        -----
        Supports both CLI flags and environment variable overrides.
        """
        group.add_argument(
            "--lt-otel-exporter-otlp-endpoint",
            type=str,
            help=(
                "OpenTelemetry OTLP exporter endpoint for Locust metrics "
                "(e.g., http://otel-collector:4317)"
            ),
            env_var="LOCUST_OTEL_EXPORTER_OTLP_ENDPOINT",
            default="",
        )
        group.add_argument(
            "--lt-otel-exporter-otlp-insecure",
            type=bool,
            help="Use insecure (non-TLS) connection to the OpenTelemetry OTLP endpoint",
            env_var="LOCUST_OTEL_EXPORTER_OTLP_INSECURE",
            default=False,
        )
        group.add_argument(
            "--lt-otel-trace-injection-by-header",
            type=bool,
            help=(
                "Enable OpenTelemetry trace propagation via HTTP headers. "
                "Use this option if no OTLP exporter is available, so trace context "
                "is still injected into Locust requests for downstream correlation."
            ),
            env_var="LOCUST_OTEL_TRACE_INJECTION_BY_HEADER",
            default=True,
        )

    def load_master_telemetry_recorders(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Load and initialize the OpenTelemetry recorder for the Locust master node.

        Parameters
        ----------
        environment : Environment
            The Locust runtime environment.
        **kwargs : Any
            Additional keyword arguments passed from the plugin system.
        """
        MasterLocustOtelRecorder(env=environment)

    def load_worker_telemetry_recorders(
        self, environment: Environment, **kwargs: Any
    ) -> None:
        """
        Load and initialize the OpenTelemetry recorder for Locust worker nodes.

        Parameters
        ----------
        environment : Environment
            The Locust runtime environment.
        **kwargs : Any
            Additional keyword arguments passed from the plugin system.
        """
        WorkerLocustOtelRecorder(env=environment)
