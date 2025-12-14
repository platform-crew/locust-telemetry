.. _telemetry:

Metrics Recorders
==================

Json Telemetry Recorder
--------------------------

The JSON recorder plugin emits structured telemetry logs that can be easily
ingested into log-based observability tools such as Elasticsearch, Loki,
Splunk, or any JSON-compatible pipeline.

It focuses on **structured events and metrics** rather than time-series
metrics, making it suitable for lightweight setups or environments where
OpenTelemetry is not available.

The plugin produces two main categories of telemetry data:

- **Events** – lifecycle and system-level signals (e.g. test start, stop,
  spawning complete, CPU warnings).
- **Metrics / Request Stats** – periodic performance data such as system usage
  and aggregated request statistics.

For a complete list of Locust’s native events, refer to the official
`Locust documentation <https://docs.locust.io/en/stable/>`_.

This plugin extends those capabilities by emitting additional **telemetry
events** and **metrics** in JSON format.

.. note::
   - This telemetry corresponds to the recorder plugin ``json``
   - To enable this recorder, use either CLI or environment variables:
     ``LOCUST_ENABLE_TELEMETRY_RECORDER=json`` or
     ``--enable-telemetry-recorder json``


The following telemetry events and metrics are emitted by the ``json`` plugin:


**Lifecycle Events:**

Lifecycle events are emitted as structured JSON log entries.

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - **Name**
     - **Source**
     - **Description**
   * - ``locust.tl.event.test.start``
     - Master
     - Emitted when the test run starts
   * - ``locust.tl.event.test.stop``
     - Master
     - Emitted when the test run stops
   * - ``locust.tl.event.spawn.complete``
     - Master
     - Emitted after all users have been spawned
   * - ``locust.tl.event.cpu.warning``
     - Master / Worker
     - Emitted when CPU usage crosses the configured warning threshold


**System Metrics:**

System metrics are emitted periodically as structured JSON logs.

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - **Name**
     - **Source**
     - **Description**
   * - ``locust.tl.system.metric.cpu``
     - Master / Worker
     - Current CPU usage on the master or worker
   * - ``locust.tl.system.metric.mem``
     - Master / Worker
     - Current memory usage on the master or worker
   * - ``locust.tl.system.metric.network``
     - Master / Worker
     - Current network usage on the master or worker


**Request Metrics:**

Request metrics are emitted as aggregated statistics in JSON format.

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - **Name**
     - **Source**
     - **Description**
   * - ``locust.tl.request.metric.stats``
     - Master
     - Aggregated request statistics, including per-endpoint metrics and error
       counts

OpenTelemetry Metrics Recorder
----------------------------------

The OpenTelemetry recorder plugin exports Locust telemetry using the
OpenTelemetry (OTel) metrics API. This enables seamless integration with
existing observability backends such as Prometheus, Grafana, Datadog,
New Relic, or any OTLP-compatible collector.

Unlike the JSON recorder, the OpenTelemetry recorder plugin focuses on
**metrics-based observability** rather than structured logs.

It supports both **master** and **worker** nodes and exports metrics via
an OTLP exporter at a configurable interval.

.. note::
   - This telemetry corresponds to the recorder plugin ``otel``
   - To enable this recorder, use either CLI or environment variables:
     ``LOCUST_ENABLE_TELEMETRY_RECORDER=otel`` or
     ``--enable-telemetry-recorder otel``


The following telemetry metrics and events are emitted by the ``otel`` plugin:

**Lifecycle Events (Counters)**

Lifecycle events are recorded as **counters** with the event type attached
as an attribute.

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - **Metric Name**
     - **Source**
     - **Description**
   * - ``locust.tl.event.test.events``
     - Master
     - Counter instrument recording test lifecycle events (start, stop, spawn complete). Event type provided via ``event`` attribute.


**System Metrics (Observable Gauges)**

System-level metrics are collected periodically using **observable gauges**.

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - **Metric Name**
     - **Source**
     - **Description**
   * - ``locust.tl.system.metric.cpu``
     - Master / Worker
     - ObservableGauge capturing CPU usage (%) of the Locust process
   * - ``locust.tl.system.metric.mem``
     - Master / Worker
     - ObservableGauge capturing memory usage (MiB) of the Locust process
   * - ``locust.tl.system.metric.network``
     - Master / Worker
     - ObservableGauge capturing network I/O (bytes sent/received). Attribute ``direction`` indicates sent or recv.


**Request Metrics (Histograms)**

Request metrics are recorded using **histograms** to capture latency
distributions.

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - **Metric Name**
     - **Source**
     - **Description**
   * - ``locust.tl.request.metric.success``
     - Master
     - Histogram recording durations (ms) of successful requests
   * - ``locust.tl.request.metric.error``
     - Master
     - Histogram recording durations (ms) of failed requests


**User Metrics (Observable Gauges)**

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - **Metric Name**
     - **Source**
     - **Description**
   * - ``locust.tl.user.metric.count``
     - Master
     - ObservableGauge capturing the current active user count


.. note::
   - OpenTelemetry **traces and spans are not yet supported**
   - Trace/span support is planned and contributions are welcome
