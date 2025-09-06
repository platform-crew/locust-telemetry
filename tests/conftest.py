from unittest.mock import MagicMock

import pytest
from locust.env import Environment


@pytest.fixture
def mock_env():
    env = MagicMock(
        spec=Environment,
        runner=MagicMock(),
        run_id="1234",
        parsed_options=MagicMock(
            testplan="test-plan",
            num_users=10,
            profile="default",
            wait_after_test_stop=0.1,
            recorder_interval=1,
        ),
        stats=MagicMock(total=MagicMock(), entries={}, errors={}),
        events=MagicMock(),
    )

    for event_name in ["test_start", "test_stop", "spawning_complete"]:
        event_mock = MagicMock()
        setattr(env.events, event_name, event_mock)
        event_mock.add_listener = MagicMock()
    return env
