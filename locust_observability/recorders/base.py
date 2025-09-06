"""
Base Recorder for Locust Observability

This module provides the `BaseRecorder` class, which serves as the base class
for all metrics recorders in a Locust environment.

All custom recorders should inherit from this class to ensure they have the
mandatory logging structure and access to the Locust environment context.
"""

import logging
from typing import Any, ClassVar

from locust.env import Environment

from locust_observability.metrics import MetricData

logger = logging.getLogger(__name__)


class BaseRecorder:
    """
    Base class for metrics recorders.

    Provides:
    - Access to the Locust environment.
    - Standardized method to log structured metrics with environment context.

    Attributes:
        name (ClassVar[str]): Identifier for the recorder. Should be overridden
        by subclasses.
        env (Environment): The Locust environment instance.
    """

    name: ClassVar[str] = "base"

    def __init__(self, env: Environment) -> None:
        """
        Initialize the base recorder with the Locust environment.

        Args:
            env (Environment): The Locust environment instance.
        """
        self.env = env

    def log_metrics(self, metric: MetricData, **kwargs: Any) -> None:
        """
        Log a structured metric event with context from the Locust environment.

        Args:
            metric (MetricData): The metric data to log.
            **kwargs: Additional metric attributes to include in the log.
        """
        logger.info(
            f"Logging {metric.name} metrics",
            extra={
                "metrics": {
                    "run_id": getattr(self.env, "run_id", None),
                    "metric_type": metric.type,
                    "metric_name": metric.name,
                    "recorder": self.name,
                    "testplan": getattr(self.env.parsed_options, "testplan", None),
                    **kwargs,
                }
            },
        )
