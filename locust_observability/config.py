"""
Locust-Observability Configuration

This module defines:
- Default interval settings for stats recording and test stop buffering
- Master and worker recorder class references

Constants:
- DEFAULT_OB_RECORDER_INTERVAL: default interval (seconds) for recording stats
- DEFAULT_OB_WAIT_AFTER_TEST_STOP: buffer time after test stop (seconds)
  for log visualization

Recorder Tuples:
- MASTER_NODE_RECORDERS: tuple of recorders for master node
- WORKER_NODE_RECORDERS: tuple of recorders for worker node
"""

from locust_observability.recorders.stats import MasterNodeStatsRecorder
from locust_observability.recorders.system import WorkerNodeStatsRecorder

# Default intervals
DEFAULT_OB_RECORDER_INTERVAL = 2  # seconds
DEFAULT_OB_WAIT_AFTER_TEST_STOP = 0.5  # seconds

# -------------------------------
# Recorder Definitions
# -------------------------------
MASTER_NODE_RECORDERS = (MasterNodeStatsRecorder,)
WORKER_NODE_RECORDERS = (WorkerNodeStatsRecorder,)
