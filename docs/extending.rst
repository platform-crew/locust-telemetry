Extending Locust Telemetry
==========================

Locust Telemetry is designed to be easily extendable. This guide explains
how to create custom telemetry recorder plugins and recorders to capture
metrics, events, or system data during your Locust tests.

Overview
--------

The telemetry system consists of:

- **TelemetryCoordinator**: Singleton responsible for lifecycle coordination
  between master and worker nodes.
- **TelemetryRecorderPluginManager**: Singleton that manages recorder plugin
  registration and loading.
- **TelemetryRecorderPluginBase**: Base class for all telemetry recorder
  plugins.
- **TelemetryBaseRecorder**: Base class for telemetry recorders (metrics or events).

This layered design allows developers to create plugins that register multiple
recorders, each running on master or worker nodes.

Creating a Telemetry Recorder Plugin
-----------------------------------

A telemetry recorder plugin manages one or more recorders and provides CLI
integration.

1. Inherit from ``TelemetryRecorderPluginBase``.

2. Define a unique ``RECORDER_PLUGIN_ID``.

3. Override methods to register CLI arguments and master/worker recorders.

Example
^^^^^^^^

.. code-block:: python

    from locust_telemetry.core.plugin import TelemetryRecorderPluginBase
    from locust_telemetry.recorder import TelemetryBaseRecorder
    from locust.env import Environment

    class CustomTelemetryRecorder(TelemetryBaseRecorder):
        name = "custom_recorder"

        def record_event(self, data):
            self.log_telemetry(data, source="custom")

    @telemetry_recorder_plugin
    class CustomTelemetryPlugin(TelemetryRecorderPluginBase):
        RECORDER_PLUGIN_ID = "custom_plugin"

        def add_cli_arguments(self, group):
            group.add_argument(
                "--custom-interval",
                type=int,
                help="Custom interval for recording metrics",
                default=5,
            )

        def load_master_telemetry_recorders(self, environment: Environment, **kwargs):
            CustomTelemetryRecorder(env=environment)

        def load_worker_telemetry_recorders(self, environment: Environment, **kwargs):
            CustomTelemetryRecorder(env=environment)

Registering the Plugin
---------------------

Use the ``@telemetry_recorder_plugin`` decorator to automatically register
your plugin with the `TelemetryRecorderPluginManager`.

This ensures that it is loaded during Locust's init phase when
`TelemetryCoordinator` calls `load_recorder_plugins`.

Creating a Custom Recorder
--------------------------

If your plugin requires custom data collection:

1. Inherit from ``TelemetryBaseRecorder``.
2. Override methods or add new methods to capture and log telemetry.
3. Use ``self.env`` for Locust environment access and ``self.log_telemetry()`` for logging.

Example
^^^^^^^^

.. code-block:: python

    class WorkerMetricsRecorder(TelemetryBaseRecorder):
        name = "worker_metrics"

        def record_metrics(self, metrics):
            self.log_telemetry(metrics, node_type="worker")

Best Practices
--------------

* Keep each recorder **focused** on a single responsibility (e.g., metrics, events, integrations).
* Use **structured logs** via ``log_telemetry`` for consistent context.
* Add **CLI arguments** via ``add_cli_arguments`` instead of hardcoding values.
* Respect **master/worker separation** and recorder lifecycle events.
* Test in both **master** and **worker** modes for distributed compatibility.
* Keep plugins **modular** and use a unique ``RECORDER_PLUGIN_ID``.
* Include sufficient **context** (run ID, testplan, environment) in logs.
* Contribute useful recorders back to the community 🚀


References
----------

- See `TelemetryCoordinator` for lifecycle management.
- See `TelemetryRecorderPluginManager` for plugin registration and loading.
- Refer to :ref:`quickstart` for setup instructions.
