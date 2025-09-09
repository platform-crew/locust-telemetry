from unittest.mock import patch

import pytest

from locust_telemetry import metadata


def test_set_test_metadata_sets_attributes(mock_env):
    """Ensure set_test_metadata sets all attributes from config generators."""
    fake_generators = {
        "run_id": lambda: "test-run",
        "env": lambda: "dev",
    }
    with patch.dict(
        metadata.config.__dict__, {"ENVIRONMENT_METADATA": fake_generators}
    ):
        metadata.set_test_metadata(mock_env)
        for key, gen in fake_generators.items():
            assert getattr(mock_env, key) == gen()


def test_set_test_metadata_does_overwrite_existing(mock_env):
    """Ensure set_test_metadata does not overwrite already set attributes."""
    fake_generators = {"run_id": lambda: "new-run"}
    mock_env.run_id = "existing-run"

    with patch.dict(
        metadata.config.__dict__, {"ENVIRONMENT_METADATA": fake_generators}
    ):
        metadata.set_test_metadata(mock_env)
        # Value should remain unchanged
        assert mock_env.run_id == "new-run"


def test_get_test_metadata_returns_all_keys(mock_env):
    """Ensure get_test_metadata returns correct key/value pairs."""
    fake_generators = {
        "run_id": lambda: "test-run",
        "env": lambda: "dev",
    }
    with patch.dict(
        metadata.config.__dict__, {"ENVIRONMENT_METADATA": fake_generators}
    ):
        metadata.set_test_metadata(mock_env)
        md = metadata.get_test_metadata(mock_env)
        assert md["run_id"] == "test-run"
        assert md["env"] == "dev"


def test_get_test_metadata_raises_if_missing_key(mock_env):
    """Ensure get_test_metadata raises AttributeError if metadata key is missing."""
    fake_generators = {"run_id": lambda: "test-run", "env": lambda: "dev"}
    with patch.dict(
        metadata.config.__dict__, {"ENVIRONMENT_METADATA": fake_generators}
    ):
        setattr(mock_env, "run_id", "1234")
        if hasattr(mock_env, "env"):
            delattr(mock_env, "env")

        with pytest.raises(AttributeError) as exc_info:
            metadata.get_test_metadata(mock_env)
        assert "env" in str(exc_info.value)


def test_apply_worker_metadata_sets_attributes(mock_env, sample_metadata):
    """
    Ensure apply_worker_metadata sets attributes correctly on the
    worker environment.
    """
    metadata.apply_worker_metadata(mock_env, sample_metadata)
    for key, value in sample_metadata.items():
        assert getattr(mock_env, key) == value


def test_apply_worker_metadata_overwrites_existing(mock_env, sample_metadata):
    """Ensure apply_worker_metadata overwrites existing values."""
    mock_env.run_id = "old-run"
    sample_metadata["run_id"] = "new-run"

    metadata.apply_worker_metadata(mock_env, sample_metadata)
    assert getattr(mock_env, "run_id") == "new-run"


def test_apply_worker_metadata_logs_info(mock_env, sample_metadata):
    """Ensure apply_worker_metadata logs an info message after applying metadata."""
    with patch("locust_telemetry.metadata.logger.info") as mock_info:
        metadata.apply_worker_metadata(mock_env, sample_metadata)
        mock_info.assert_called_once()
        args, kwargs = mock_info.call_args
        assert "Metadata applied" in args[0]
        assert getattr(mock_env, "run_id") in args
        assert getattr(mock_env.parsed_options, "testplan") in args
