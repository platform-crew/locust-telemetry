"""
Locust-Observability Initialization and Recorder Setup

This module handles the initialization of the Locust-Observability plugin, including:

- Logging configuration
- Test-metadata generation
- Master and worker recorder registration
- Command-line argument extensions for Locust
"""

import logging
from typing import Any

from locust import events
from locust.argument_parser import LocustArgumentParser
from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

from locust_observability import config
from locust_observability.logger import configure_logging
from locust_observability.metadata import (
    get_test_metadata,
    handle_worker_metadata,
    set_test_metadata,
)

logger = logging.getLogger(__name__)

# -------------------------------
# Command-line Argument Extensions
# -------------------------------


@events.init_command_line_parser.add_listener
def add_arguments(parser: LocustArgumentParser) -> None:
    """
    Add locust-observability-specific command-line arguments and environment variables.

    Args:
        parser (LocustArgumentParser): The Locust argument parser to extend.
    """
    group = parser.add_argument_group(
        "locust-observability - Extra environment variables",
        "Environment variables for configuring Locust observability plugin",
    )

    group.add_argument(
        "--testplan",
        type=str,
        help="Unique identifier for the tests or service name under test.",
        env_var="LOCUST_TESTPLAN_NAME",
        required=True,
    )

    group.add_argument(
        "--recorder-interval",
        type=int,
        help="Interval (in seconds) for recorder updates.",
        env_var="LOCUST_OB_RECORDER_INTERVAL",
        default=config.DEFAULT_OB_RECORDER_INTERVAL,
    )

    group.add_argument(
        "--wait-after-test-stop",
        type=float,
        help=(
            "Wait after test stop to ensure logs are processed "
            "(buffer for visualization)"
        ),
        env_var="LOCUST_OB_WAIT_AFTER_TEST_STOP",
        default=config.DEFAULT_OB_WAIT_AFTER_TEST_STOP,
    )


# -------------------------------
# Logging Setup
# -------------------------------


@events.init.add_listener
def setup_logging(environment: Environment, **kwargs: Any) -> None:
    """
    Configure JSON logging for master and worker processes.

    Args:
        environment (Environment): Locust environment object.
        **kwargs: Additional keyword arguments from the event.
    """
    configure_logging()
    logger.info(
        "[%s] Logging configured successfully.", environment.runner.__class__.__name__
    )


# -------------------------------
# Master Initialization
# -------------------------------


@events.test_start.add_listener
def setup_master_test(environment: Environment, **kwargs: Any) -> None:
    """
    Master process initialization.

    This includes:
    - Generating and attaching test metadata
    - Registering master recorders
    - Broadcasting metadata to connected workers

    Args:
        environment (Environment): Locust environment object.
        **kwargs: Additional keyword arguments from the event.
    """
    if not isinstance(environment.runner, MasterRunner):
        return

    metadata = get_test_metadata()
    set_test_metadata(environment, metadata)

    for recorder in config.MASTER_NODE_RECORDERS:
        recorder(env=environment)

    logger.info("Sending test metadata to workers", extra={"metadata": metadata})
    environment.runner.send_message("set_metadata", metadata)


# -------------------------------
# Worker Initialization
# -------------------------------


@events.init.add_listener
def init_worker(environment: Environment, **kwargs: Any) -> None:
    """
    Worker process initialization.

    This includes:
    - Registering a handler to receive metadata from the master
    - Initializing worker-specific recorders after receiving metadata

    Args:
        environment (Environment): Locust environment object.
        **kwargs: Additional keyword arguments from the event.
    """
    if not isinstance(environment.runner, WorkerRunner):
        return

    environment.runner.register_message(
        "set_metadata",
        lambda msg, **kw: handle_worker_metadata(environment, msg.data),
    )

    logger.info("[Worker] Metadata handler registered successfully.")
