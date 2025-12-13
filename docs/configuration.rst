.. _configuration:

Configuration
===============

The core configuration of Locust remains unchanged. However, this plugin
introduces a few additional environment variables.

To view all available locust configuration, please refer `here <https://docs.locust.io/en/stable/configuration.html>`_
or use below command

.. code-block:: bash

   $locust --help

.. warning::

   Since Locust does not currently support plugin-specific options, locust-telemetry
   configuration variables will **not** appear in the ``--help``
   output. Support for plugin options is planned for a future release. For now please refer below table.


.. list-table::
   :header-rows: 1
   :widths: 18 26 10 10 10 26

   * - **CLI**
     - **Environment Variable**
     - **Default**
     - **Required**
     - **Plugin**
     - **Description**
   * - ``--testplan``
     - ``LOCUST_TESTPLAN_NAME``
     - *N/A*
     - Yes
     - json / otel
     - Unique identifier for the test run
   * - ``--enable-telemetry-recorder``
     - ``LOCUST_ENABLE_TELEMETRY_RECORDER``
     - ``json``
     - No
     - json / otel
     - Telemetry recorder to use: ``json`` or ``otel``
   * - ``--lt-stats-recorder-interval``
     - ``LOCUST_TELEMETRY_STATS_RECORDER_INTERVAL``
     - ``2``
     - No
     - json / otel
     - Interval (in seconds) for exporting telemetry metrics
   * - ``--lt-system-usage-recorder-interval``
     - ``LOCUST_TELEMETRY_SYSTEM_USAGE_RECORDER_INTERVAL``
     - ``2``
     - No
     - json / otel
     - Interval (in seconds) for system usage monitoring
   * - ``--lt-otel-exporter-otlp-endpoint``
     - ``LOCUST_OTEL_EXPORTER_OTLP_ENDPOINT``
     - *N/A*
     - No
     - otel
     - OTLP gRPC endpoint for exporting OpenTelemetry metrics
   * - ``--lt-otel-exporter-otlp-insecure``
     - ``LOCUST_OTEL_EXPORTER_OTLP_INSECURE``
     - ``False``
     - No
     - otel
     - Use insecure (non-TLS) connection for the OTLP exporter


The package also provides an entry point that can be used for auto
discovery and loading. However, this requires corresponding
changes on the Locust side.

.. code-block:: bash

   [project.entry-points."locust_plugins"]
   telemetry_locust = "locust_telemetry.entrypoint"
