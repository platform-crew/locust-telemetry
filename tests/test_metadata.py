from locust_telemetry.metadata import set_test_metadata


def test_static_metadata(mock_env):
    """Metadata values should be attached as-is to the environment."""
    metadata = {"test_name": "load_test", "version": "1.0"}
    set_test_metadata(mock_env, metadata)

    assert hasattr(mock_env, "telemetry_meta") is True
    assert mock_env.telemetry_meta.test_name == "load_test"
    assert mock_env.telemetry_meta.version == "1.0"


def test_overrides_existing_metadata(mock_env):
    """Subsequent calls should overwrite the metadata object entirely."""
    set_test_metadata(mock_env, {"first": "one"})
    first_meta = mock_env.telemetry_meta

    set_test_metadata(mock_env, {"second": "two"})
    second_meta = mock_env.telemetry_meta

    assert not hasattr(second_meta, "first")
    assert second_meta.second == "two"
    assert first_meta is not second_meta  # replaced, not mutated
