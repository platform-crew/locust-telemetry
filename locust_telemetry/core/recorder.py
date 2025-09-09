"""

This module provides the `BaseTelemetryRecorder` class, which serves as the foundation
for all telemetry recorders (metrics or events) in a Locust environment.

Usage
-----
Custom recorders should inherit from this class to ensure:

- A consistent logging structure.
- Access to the Locust environment context.
- Standardized telemetry recording across master and worker nodes.
"""

import logging
import os
import socket
from typing import Any, ClassVar

from locust.env import Environment

from locust_telemetry.common.telemetry import TelemetryData

logger = logging.getLogger(__name__)


class BaseTelemetryRecorder:
    """
    Base class for telemetry recorders.

    Responsibilities:
    - Maintain access to the Locust environment
    - Provide a standardized logging method for structured telemetry
      (both metrics and events)

    Attributes:
        name (ClassVar[str]): Identifier for the telemetry recorder.
            Should be overridden by subclasses.
        env (Environment): The Locust environment instance.
    """

    name: ClassVar[str] = "base"

    def __init__(self, env: Environment) -> None:
        """
        Initialize the telemetry recorder with the Locust environment.

        Args:
            env (Environment): The Locust environment instance.
        """
        self.env = env
        self._username: str = os.getenv("USER", "unknown")
        self._hostname: str = socket.gethostname()
        self._pid: int = os.getpid()

    def log_telemetry(self, telemetry: TelemetryData, **kwargs: Any) -> None:
        """
        Record structured telemetry data with environment context.

        Args:
            telemetry (TelemetryData): The telemetry descriptor (event or metric)
            **kwargs: Additional attributes to include in the telemetry log
        """
        logger.info(
            f"Recording telemetry: {telemetry.name}",
            extra={
                "telemetry": {
                    "run_id": getattr(self.env, "run_id", None),
                    "telemetry_type": telemetry.type,
                    "telemetry_name": telemetry.name,
                    "recorder": self.name,
                    "testplan": getattr(self.env.parsed_options, "testplan", None),
                    **kwargs,
                }
            },
        )
