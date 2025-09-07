Quick Start
===========

Load the core telemetry plugin in your Locust test script:

.. code-block:: python

    from locust_telemetry.core_telemetry.plugin import core_plugin_load
    core_plugin_load()

For Kubernetes-specific telemetry:

.. code-block:: python

    from locust_telemetry.k8_telemetry.plugin import k8_plugin_load
    k8_plugin_load()

Your Locust load test is now instrumented with structured telemetry logging.
