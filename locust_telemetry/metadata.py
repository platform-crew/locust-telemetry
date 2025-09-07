"""
Locust Telemetry Metadata Utilities
===================================

This module provides helper functions for managing test metadata
in a Locust Telemetry setup. Metadata is generated on the master node,
propagated to worker nodes, and attached to the Locust environment.

Responsibilities
----------------
- Generate and attach metadata to the master environment
- Retrieve metadata from any environment
- Apply master-sent metadata on worker environments

Functions
---------
set_test_metadata(environment)
    Generate and attach test metadata to the Locust environment.

get_test_metadata(environment)
    Retrieve metadata from the environment as a dictionary.

apply_worker_metadata(environment, metadata)
    Apply metadata received from the master node to a worker environment.
"""

import logging
from typing import Dict

from locust.env import Environment

from locust_telemetry import config

logger = logging.getLogger(__name__)


def set_test_metadata(environment: Environment) -> None:
    """
    Generate and attach test metadata to the Locust environment.

    If a metadata key is not already present, it will be created using
    the corresponding generator function from `config.ENVIRONMENT_METADATA`.

    Args:
        environment (Environment): The Locust environment instance.
    """
    for key, generator in config.ENVIRONMENT_METADATA.items():
        setattr(environment, key, generator())


def get_test_metadata(environment: Environment) -> Dict[str, str]:
    """
    Collect all configured metadata from the Locust environment.

    Args:
        environment (Environment): The Locust environment instance.

    Raises:
        AttributeError: If a required metadata key has not been set.

    Returns:
        Dict[str, str]: A dictionary of metadata key/value pairs.
    """
    metadata = {}
    for key in config.ENVIRONMENT_METADATA:
        if not hasattr(environment, key):
            raise AttributeError(
                f"Metadata key '{key}' has not been set on the environment."
            )
        metadata[key] = getattr(environment, key)
    return metadata


def apply_worker_metadata(environment: Environment, metadata: Dict[str, str]) -> None:
    """
    Apply master-sent metadata to a worker environment.

    This function sets metadata attributes on the worker's environment,
    ensuring consistency with the master node.

    Args:
        environment (Environment): The worker environment instance.
        metadata (Dict[str, str]): Metadata dictionary sent from the master node.
    """
    for key, value in metadata.items():
        setattr(environment, key, value)

    logger.info(
        "[Worker] Metadata applied: run_id=%s, testplan=%s",
        getattr(environment, "run_id", None),
        getattr(environment.parsed_options, "testplan", None),
    )
