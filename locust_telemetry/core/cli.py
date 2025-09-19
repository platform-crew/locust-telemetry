"""
Telemetry CLI integration for Locust.

Responsibilities
----------------
- Provide a dedicated argument group for telemetry configuration.
- Register core telemetry CLI arguments (e.g., ``--testplan``).
- Ensure safe repeated registration without duplicating groups.
"""

from locust.argument_parser import LocustArgumentParser

from locust_telemetry.config import (
    DEFAULT_STATS_RECORDER_INTERVAL,
    DEFAULT_WORKER_REGION,
    TELEMETRY_CLI_GROUP_NAME,
    TELEMETRY_JSON_STATS_RECORDER_PLUGIN_ID,
    TELEMETRY_OTEL_RECORDER_PLUGIN_ID,
)


def register_telemetry_cli_args(parser: LocustArgumentParser):
    """
    Register core telemetry CLI arguments for Locust.

    This function creates (or reuses) a dedicated argument group
    for telemetry-related options. It ensures that ``--testplan``
    and ``--enable-telemetry-recorder`` are available.

    Parameters
    ----------
    parser : LocustArgumentParser
        The Locust argument parser instance.

    Returns
    -------
    _ArgumentGroup
        The argument group created for telemetry options,
        or the existing one if already registered.
    """

    group = parser.add_argument_group(
        f"{TELEMETRY_CLI_GROUP_NAME} - Locust Telemetry",
        "Configuration options for telemetry recorder plugins "
        "(can also be set via environment variables).",
    )

    group.add_argument(
        "--testplan",
        type=str,
        help="Unique identifier for the test run or service under test.",
        env_var="LOCUST_TESTPLAN_NAME",
        required=True,
    )

    group.add_argument(
        "--enable-telemetry-recorder",
        choices=[
            TELEMETRY_JSON_STATS_RECORDER_PLUGIN_ID,
            TELEMETRY_OTEL_RECORDER_PLUGIN_ID,
        ],
        help=(
            "Enable one or more telemetry recorder plugins. "
            "Comma-separated list or via environment variable."
        ),
        env_var="LOCUST_ENABLE_TELEMETRY_RECORDER",
        default=[],
        action="append",
    )

    group.add_argument(
        "--lt-stats-recorder-interval",
        type=int,
        help="Interval (in seconds) for telemetry statistics recorder updates.",
        env_var="LOCUST_TELEMETRY_STATS_RECORDER_INTERVAL",
        default=DEFAULT_STATS_RECORDER_INTERVAL,
    )

    group.add_argument(
        "--lt-worker-region",
        type=int,
        help="Worker deployed region. This can be used to identify the request "
        "from different geographical location",
        env_var="LOCUST_TELEMETRY_WORKER_REGION",
        default=DEFAULT_WORKER_REGION,
    )

    return group
