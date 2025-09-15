"""
This module provides the `TelemetryBaseRecorder` class, which serves as the foundation
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
from typing import ClassVar, Dict

from locust.env import Environment
from locust.runners import MasterRunner

logger = logging.getLogger(__name__)


class TelemetryBaseRecorder:
    """
    Base class for telemetry recorders.

    Responsibilities
    ----------------
    - Maintain access to the Locust environment.
    - Provide a standardized logging method for structured telemetry
      (both metrics and events).

    Attributes
    ----------
    name : ClassVar[str]
        Identifier for the recorder. Should be overridden by subclasses.
    env : Environment
        The Locust environment instance.
    """

    name: ClassVar[str] = "base"

    def __init__(self, env: Environment) -> None:
        """
        Initialize the base recorder with the Locust environment.

        Parameters
        ----------
        env : Environment
            The Locust environment instance.
        """
        self.env = env
        self._username: str = os.getenv("USER", "unknown")
        self._hostname: str = socket.gethostname()
        self._pid: int = os.getpid()

    def recorder_context(self) -> Dict:
        """
        Common recorder context for all the recorders. This will give the context
        on where this metrics are generated and its details
        """
        return {
            "run_id": self.env.run_id,
            "testplan": self.env.testplan,
            "source_type": self.env.runner.__class__.__name__,
            "recorder": self.name,
            "source_id": (
                "master"
                if isinstance(self.env.runner, MasterRunner)
                else f"worker-{self.env.runner.worker_index}"
            ),
        }
