.. _quickstart:

Quick Start
===========

This plugin enhances Locust with telemetry recording while preserving all existing Locust usage patterns and configuration options.
For details on Locust itself, refer to the official `Locust documentation <https://docs.locust.io/en/stable/index.html>`_.

1. **Initialize the telemetry plugin** in your Locust test script (e.g., `locustfile.py`):

.. code-block:: python

    from locust_telemetry import entrypoint
    entrypoint.initialize()

2. **Run your Locust tests** with telemetry enabled. Specify the test plan and the recorder plugin:

Json metrics recorder

.. code-block:: bash

    $ locust -f locustfile.py --testplan mytest --enable-telemetry-recorder json

OpenTelemetry metrics recorder

.. code-block:: bash

    $ locust -f locustfile.py --testplan mytest --enable-telemetry-recorder otel

.. note::
   - CLI arguments can also be configured via environment variables:

     - ``LOCUST_TESTPLAN_NAME`` → equivalent to ``--testplan``
     - ``LOCUST_ENABLE_TELEMETRY_RECORDER`` → equivalent to ``--enable-telemetry-recorder``

   - For a complete list of telemetry configuration options, see the :ref:`configuration` section.

   - For guidance on setting up Locust tests, consult the `Locust Quick Start Guide <https://docs.locust.io/en/stable/quickstart.html>`_.


.. warning::
   - Locust currently does not support plugin arguments (``--plugin`` or ``-p``).
     Therefore, plugins must be loaded manually in ``locustfile.py``.
