"""
Locust-Observability Metadata Utilities

This module provides utilities for handling test metadata in Locust-Observability:

- Generating unique test metadata
- Setting metadata on the Locust Environment
- Handling metadata received by worker nodes
"""

import logging
from datetime import datetime, timezone
from typing import Dict

from locust.env import Environment
from locust_observability import config

logger = logging.getLogger(__name__)


def get_test_metadata() -> Dict[str, str]:
    """
    Generate a unique test metadata dictionary with a UTC timestamp.

    Returns:
        Dict[str, str]: A dictionary containing the 'run_id' key with an
        ISO-formatted UTC timestamp.
    """
    return {"run_id": datetime.now(timezone.utc).isoformat()}


def set_test_metadata(environment: Environment, metadata: Dict[str, str]) -> None:
    """
    Attach metadata as attributes to the Locust environment.

    Args:
        environment (Environment): The Locust environment object to attach metadata to.
        metadata (Dict[str, str]): A dictionary of metadata key-value pairs to set.
    """
    for key, value in metadata.items():
        setattr(environment, key, value)


def handle_worker_metadata(environment: Environment, metadata: Dict[str, str]) -> None:
    """
    Apply master-sent metadata to a worker environment and initialize worker recorders.

    This function sets metadata attributes on the environment and initializes
    all worker node recorders defined in the configuration.

    Args:
        environment (Environment): The Locust worker environment object.
        metadata (Dict[str, str]): Metadata dictionary sent from the master node.
    """
    set_test_metadata(environment, metadata)

    for recorder in config.WORKER_NODE_RECORDERS:
        recorder(env=environment)  # assume recorder accepts env parameter

    testplan = getattr(environment.parsed_options, "testplan", None)
    logger.info(
        "[Worker] Metadata applied: run_id=%s, testplan=%s",
        environment.run_id,
        testplan,
    )
