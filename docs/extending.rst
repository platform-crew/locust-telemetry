Extending Guide
=======================================

``locust-telemetry`` is designed to be **easily extensible**.
You can add your own custom telemetry plugins and recorders to capture
domain-specific metrics or integrate with other observability systems.

This guide explains the main extension points and demonstrates
how to implement them effectively.

Project Repository
------------------
Source code is available on GitHub:

:link: `Locust Telemetry Repository <https://github.com/platform-crew/locust-telemetry>`_

Extension Points Overview
-------------------------
Before extending, it's important to understand the three key components:

1. **Plugins**
   - Extend :class:`locust_telemetry.core.plugin.BaseTelemetryPlugin`
   - Register CLI arguments if needed
   - Register master and worker telemetry recorders

2. **Recorders**
   - Extend :class:`locust_telemetry.core.recorder.BaseTelemetryRecorder`
   - Implement structured logging for your telemetry data
   - Attach to Locust events (``test_start``, ``test_stop``, request stats, etc.)

3. **Manager**
   - :class:`locust_telemetry.core.manager.PluginManager` handles plugin registration
   - :class:`locust_telemetry.core.manager.TelemetryManager` orchestrates plugin initialization

Creating a Custom Recorder
--------------------------
A recorder is responsible for capturing metrics or events and logging them
in a **structured format** compatible with observability pipelines.

Example: ``CustomTelemetryRecorder``

.. code-block:: python

    from locust.env import Environment
    from locust_telemetry.core.recorder import BaseTelemetryRecorder
    from locust_telemetry.common.telemetry import TelemetryData

    class CustomTelemetryRecorder(BaseTelemetryRecorder):
        name = "custom_telemetry_recorder"

        def __init__(self, env: Environment):
            super().__init__(env)
            # Register event listeners
            env.events.test_start.add_listener(self.on_test_start)
            env.events.test_stop.add_listener(self.on_test_stop)

        def on_test_start(self, *args, **kwargs):
            self.log_telemetry(
                telemetry=TelemetryData(type="event", name="CUSTOM_START"),
                message="Custom telemetry recorder started"
            )

        def on_test_stop(self, *args, **kwargs):
            self.log_telemetry(
                telemetry=TelemetryData(type="event", name="CUSTOM_STOP"),
                message="Custom telemetry recorder stopped"
            )

.. note::

   **Tip:** Keep each recorder focused on a single responsibility,
   e.g., request stats, system metrics, or external integrations.

Creating a Custom Plugin
------------------------
A plugin ties together your recorder(s) and optional CLI arguments,
making them reusable and configurable.

Example: ``CustomTelemetryPlugin``

.. code-block:: python

    import logging
    from locust.argument_parser import LocustArgumentParser
    from locust.env import Environment
    from locust_telemetry.core.plugin import BaseTelemetryPlugin

    from my_project.recorder import CustomTelemetryRecorder

    logger = logging.getLogger(__name__)

    class CustomTelemetryPlugin(BaseTelemetryPlugin):
        def add_arguments(self, parser: LocustArgumentParser) -> None:
            group = parser.add_argument_group(
                "telemetry.custom",
                "Environment variables for the custom telemetry plugin"
            )
            group.add_argument(
                "--custom-option",
                type=str,
                help="Example custom argument",
                env_var="LOCUST_CUSTOM_OPTION",
                default="default-value"
            )

        def load_master_telemetry_recorders(self, environment: Environment, **kwargs):
            CustomTelemetryRecorder(env=environment)

        def load_worker_telemetry_recorders(self, environment: Environment, **kwargs):
            CustomTelemetryRecorder(env=environment)

Registering the Plugin
----------------------
Finally, register your plugin with the ``PluginManager`` at test startup:

.. code-block:: python

    from locust_telemetry.core.manager import PluginManager, TelemetryManager
    from my_project.plugin import CustomTelemetryPlugin

    def entry_point(*args, **kwargs):
        plugin_manager = PluginManager()
        plugin_manager.register_plugin(plugin=CustomTelemetryPlugin())
        telemetry_manager = TelemetryManager(plugin_manager=plugin_manager)
        telemetry_manager.initialize()

Best Practices
--------------
* Keep recorders **focused** on a single responsibility (e.g., system metrics, request stats, external integrations).
* Use **structured JSON logs** via the `log_telemetry` method provided by `BaseTelemetryRecorder`.
* Add **CLI arguments** for configurability instead of hardcoding values.
* Handle the **lifecycle of events** within each recorder to avoid unintended side effects.
* Test your plugin in both **master** and **worker** modes to ensure full compatibility.
* Consider contributing your plugin back if it could be useful for the community 🚀

.. note::

   **Pro Tip:** Early contributors often shape the project.
   Even a small telemetry plugin can help others gain deeper insights from their Locust tests.
