.. _quickstart:

Quick Start
===========

This extension enhances Locust with telemetry recording while preserving all existing Locust usage patterns and configuration options.
For details on Locust itself, refer to the official `Locust documentation <https://docs.locust.io/en/stable/index.html>`_.

1. **Initialize the telemetry plugin** in your Locust test script (e.g., `locustfile.py`):

.. code-block:: python

    from locust_telemetry import entrypoint
    entrypoint.initialize()

2. **Run your Locust tests** with telemetry enabled. Specify the test plan and the recorder plugin:

.. code-block:: bash

    $ locust -f locustfile.py --testplan mytest --enable-telemetry-recorder stats

.. note::
   - CLI arguments can also be configured via environment variables:

     - ``LOCUST_TESTPLAN_NAME`` → equivalent to ``--testplan``
     - ``LOCUST_ENABLE_TELEMETRY_RECORDER`` → equivalent to ``--enable-telemetry-recorder``

   - For a complete list of telemetry configuration options, see the :ref:`configuration` section.

   - For guidance on setting up Locust tests, consult the `Locust Quick Start Guide <https://docs.locust.io/en/stable/quickstart.html>`_.


.. warning::
   - Locust currently does not support plugin arguments (``--plugin`` or ``-p``).
     Therefore, plugins must be loaded manually in ``locustfile.py``.
   - The Locust team is planning to add native support for CLI and environment variables for plugins, which will allow direct plugin specification in the run command. Track progress in issue `#3212 <https://github.com/locustio/locust/issues/3212>`_.

Here’s an example of a Grafana dashboard built using telemetry from this plugin.
It shows how Locust metrics can be transformed into meaningful insights with just a few steps.

For a full walkthrough on setting up dashboards locally, see the :ref:`examples-section`.

.. image:: _static/request-dashboard-1.png
   :alt: Request Dashboard - Overview
   :width: 100%
   :align: center

.. image:: _static/request-dashboard-2.png
   :alt: Request Dashboard
   :width: 100%
   :align: center

.. raw:: html

   <br><br>
