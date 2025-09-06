from unittest.mock import patch

from locust_observability.metrics import MetricData
from locust_observability.recorders.base import BaseRecorder


def test_base_recorder_init(mock_env):
    """Test that BaseRecorder stores the environment correctly."""
    recorder = BaseRecorder(mock_env)
    assert recorder.env == mock_env
    assert recorder.name == "base"


@patch("locust_observability.recorders.base.logger")
def test_log_metrics_calls_logger(mock_logger, mock_env):
    """Test that log_metrics logs a message with correct extra metrics."""
    recorder = BaseRecorder(mock_env)
    metric = MetricData(type="metric", name="test_metric")

    recorder.log_metrics(metric, custom_field="value")

    # Ensure logger.info was called once
    mock_logger.info.assert_called_once()

    # Check log message
    args, kwargs = mock_logger.info.call_args
    assert args[0] == f"Logging {metric.name} metrics"

    # Check that extra dictionary contains expected keys
    extra = kwargs.get("extra", {}).get("metrics", {})
    assert extra["run_id"] == "1234"
    assert extra["metric_type"] == "metric"
    assert extra["metric_name"] == "test_metric"
    assert extra["recorder"] == "base"
    assert extra["testplan"] == "test-plan"
    assert extra["custom_field"] == "value"
