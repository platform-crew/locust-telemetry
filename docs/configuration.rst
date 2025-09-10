Configuration
=======================

The core configuration of Locust remains unchanged. However, this plugin
introduces a few additional environment variables.

To view all available locust configuration, please refer `here <https://docs.locust.io/en/stable/configuration.html>`_
or use below command

.. code-block:: bash

   $locust --help

.. note::

   Since Locust does not currently support plugin-specific options, locust-telemetry
   configuration variables will **not** appear in the ``--help``
   output. Support for plugin options is planned for a future release. For now please refer below table.



.. list-table::
   :header-rows: 1
   :widths: 25 25 8 12 10 35

   * - **Command Line**
     - **Environment Variable**
     - **Type**
     - **Default**
     - **Required**
     - **Description**
   * - ``--testplan``
     - ``LOCUST_TESTPLAN_NAME``
     - ``str``
     - *N/A*
     - Yes
     - Unique identifier for the test run or the service
       under test. This value is mandatory and must be
       provided for every execution.
   * - ``--lt-stats-recorder-interval``
     - ``LOCUST_TELEMETRY_STATS_RECORDER_INTERVAL``
     - ``int``
     - ``2``
     - No
     - Interval (in seconds) for telemetry stats recorder
       updates. If not specified, the default interval
       of ``2`` seconds will be applied.
   * - ``--lt-system-usage-recorder-interval``
     - ``LOCUST_TELEMETRY_SYSTEM_USAGE_RECORDER_INTERVAL``
     - ``int``
     - ``2``
     - No
     - Interval (seconds) for system usage monitoring.
       If not specified, the default interval
       of ``2`` seconds will be applied.



The package also provides an entry point that can be used for automatic plugin
discovery and loading. However, this requires corresponding
changes on the Locust side.

.. code-block:: bash

   [project.entry-points."locust_plugins"]
   telemetry_locust = "locust_telemetry.core_telemetry.plugin:entry_point"
