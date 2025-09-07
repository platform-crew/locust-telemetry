from locust.argument_parser import LocustArgumentParser
from locust.env import Environment

from locust_telemetry import config
from locust_telemetry.core.manager import TelemetryPluginManager
from locust_telemetry.k8_telemetry.plugin import K8TelemetryPlugin, k8_plugin_load


def test_add_arguments_creates_parser_group(parser: LocustArgumentParser) -> None:
    """Ensure K8TelemetryPlugin registers its CLI argument group correctly."""
    plugin = K8TelemetryPlugin()
    plugin.add_arguments(parser)

    found_group = False
    for group in parser._action_groups:
        if "telemetry.k8 - Locust Metrics" in group.title:
            found_group = True
            break

    assert found_group, "K8 telemetry parser group not found"

    arg_names = [a.option_strings[0] for a in group._group_actions]
    assert "--k8-telemetry-recorder-interval" in arg_names
    # Default value check
    for action in group._group_actions:
        if action.option_strings[0] == "--k8-telemetry-recorder-interval":
            assert action.default == config.DEFAULT_RECORDER_INTERVAL


def test_register_master_and_worker_do_nothing(mock_env: Environment) -> None:
    """
    Ensure register_master_telemetry_recorder and worker methods run without error.
    """
    plugin = K8TelemetryPlugin()
    plugin.register_master_telemetry_recorder(mock_env)
    plugin.register_worker_telemetry_recorder(mock_env)


def test_k8_plugin_load_registers_plugin_in_manager() -> None:
    """Ensure k8_plugin_load adds a K8TelemetryPlugin to the manager."""
    manager = TelemetryPluginManager()
    assert len(manager._plugins) == 0

    k8_plugin_load()
    assert any(isinstance(p, K8TelemetryPlugin) for p in manager._plugins)
