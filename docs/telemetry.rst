.. _telemetry:

Telemetry Recorders
==============================

Locust Json
--------------

Locust Json Telemetry plugin produces two main types of structured logs:

- **Events** – lifecycle and system-level signals (e.g., test start, stop, CPU warnings).
- **Metrics / Request Stats** – periodic performance data such as request rates, latencies, and error counts.

For a complete list of Locust’s native events, refer to the official
`Locust documentation <https://docs.locust.io/en/stable/>`_.

This plugin extends those capabilities by emitting additional **telemetry events**
and **metrics** in JSON format, making it easy to ingest into your observability tools.

.. note::
   - This telemetry is corresponding to the recorder plugin ``stats-json``
   - To select this recorder plugin you should use cli or env variables as ``LOCUST_ENABLE_TELEMETRY_RECORDER=stats-json`` OR ``--enable-telemetry-recorder stats-json``

Events
~~~~~~~~~~~~~~~~~~~~

The following telemetry events are emitted by the **locust-telemetry** plugin:

.. list-table::
   :header-rows: 1
   :widths: 15 25 20 40

   * - Type
     - Name
     - Source
     - Sample JSON
   * - event
     - event.test.start
     - Master
     - See example below
   * - event
     - event.test.stop
     - Master
     - See example below
   * - event
     - event.spawn.complete
     - Master
     - See example below
   * - event
     - event.cpu.warning
     - Master / Worker
     - See example below
   * - event
     - event.system.usage
     - Master / Worker
     - See example below


**Events Examples**

**Test Start**

.. code-block:: json

   {
     "time": "2025-09-09T17:22:06.216Z",
     "level": "INFO",
     "name": "locust_telemetry.core.recorder",
     "message": "Recording telemetry: event.test.start",
     "telemetry": {
       "run_id": "8d7b5901",
       "telemetry_type": "event",
       "telemetry_name": "event.test.start",
       "recorder": "master_locust_telemetry_recorder",
       "testplan": "myapp",
       "num_clients": 5,
       "username": "unknown"
     }
   }

**Test Stop**

.. code-block:: json

   {
     "telemetry": {
       "telemetry_name": "event.test.stop",
       "testplan": "myapp",
       "endtime": "2025-09-09T17:23:09.232Z",
       "text": "myapp finished. Stopping the tests."
     }
   }

**Spawn Complete**

.. code-block:: json

   {
     "telemetry": {
       "telemetry_name": "event.spawn.complete",
       "testplan": "myapp",
       "user_count": 5,
       "text": "myapp ramp-up complete, 5 users spawned"
     }
   }

**CPU Warning**

.. code-block:: json

   {
     "telemetry": {
       "telemetry_name": "event.cpu.warning",
       "testplan": "myapp",
       "source_type": "WorkerRunner",
       "source_id": "worker-0",
       "cpu_usage": 90.7,
       "text": "myapp high CPU usage (90%)"
     }
   }

**System Usage**

.. code-block:: json

   {
     "telemetry": {
       "telemetry_name": "event.system.usage",
       "testplan": "myapp",
       "source_type": "MasterRunner",
       "source_id": "master",
       "cpu_usage": 1.5,
       "memory_usage": 52.04
     }
   }


Metrics
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 30 15 40

   * - Type
     - Name
     - Source
     - Sample JSON
   * - metric
     - metric.request.current.stats
     - Master
     - See example below
   * - metric
     - metric.request.final.stats
     - Master
     - See example below
   * - metric
     - metric.request.endpoint.stats
     - Master
     - See example below
   * - metric
     - metric.request.endpoint.errors
     - Master
     - See example below


**Metrics Examples**

**Current Stats**

.. code-block:: json

   {
     "time": "2025-09-09T17:23:06.347Z",
     "level": "INFO",
     "name": "locust_telemetry.core.recorder",
     "message": "Recording telemetry: metric.request.current.stats",
     "telemetry": {
       "run_id": "8d7b5901",
       "telemetry_type": "metric",
       "telemetry_name": "metric.request.current.stats",
       "recorder": "master_locust_telemetry_recorder",
       "testplan": "myapp",
       "user_count": 0,
       "method": "",
       "name": "Aggregated",
       "num_requests": 88,
       "num_failures": 11,
       "min_response_time": 121.0,
       "max_response_time": 5770.0,
       "current_rps": 1.5,
       "current_fail_per_sec": 0.2,
       "avg_response_time": 1575.43,
       "median_response_time": 1200.0,
       "total_rps": 1.49,
       "total_fail_per_sec": 0.18,
       "avg_content_length": 1063.95,
       "percentile_95": 4000.0,
       "percentile_99": 5800.0
     }
   }

**Final Stats**

.. code-block:: json

   {
     "telemetry": {
       "telemetry_name": "metric.request.final.stats",
       "num_requests": 88,
       "num_failures": 11,
       "avg_response_time": 1575.43,
       "percentile_95": 4000.0,
       "percentile_99": 5800.0
     }
   }

**Endpoint Stats**

.. code-block:: json

   {
     "telemetry": {
       "telemetry_name": "metric.request.endpoint.stats",
       "request_path": "/redirect-to?url=/get",
       "method": "GET",
       "num_requests": 6,
       "num_failures": 0,
       "avg_response_time": 1693.70,
       "percentile_95": 2500.0,
       "percentile_99": 2500.0
     }
   }

**Endpoint Errors**

.. code-block:: json

   {
     "telemetry": {
       "telemetry_name": "metric.request.endpoint.errors",
       "method": "GET",
       "name": "/status/500",
       "error": "HTTPError('502 Server Error: Bad Gateway for url: /status/500')",
       "occurrences": 1
     }
   }
