"""
This module provides helper functions for managing test metadata
in a Locust Telemetry setup. Metadata is generated on the master node,
propagated to worker nodes, and attached to the Locust environment.
"""

import logging
from typing import Dict

from locust.env import Environment

logger = logging.getLogger(__name__)


def set_test_metadata(environment: Environment, metadata: Dict) -> None:
    """
    This function attaches the given
    metadata to the environment (environment.telemetry_meta). Metadata should be a
    dictionary where the values can either callable or static value.

    Args:
        environment (Environment): The Locust environment instance.
        metadata (Dict): Dict items will be set as metadata (environment.telemetry_meta)
    """
    telemetry_meta = type("", (object,), {})
    for key, val in metadata.items():
        setattr(telemetry_meta, key, val)

    logger.info(
        f"Setting metadata for {environment.runner.__class__.__name__}", extra=metadata
    )
    environment.telemetry_meta = telemetry_meta
