What is Locust Telemetry?
==========================

Locust Telemetry is a modular plugin for Locust that provides structured
observability for load and performance tests. It captures telemetry data in a
flexible, structured format, enabling integration with existing observability
tools and delivering detailed insights into system performance.

Load testing often requires correlating metrics with infrastructure data—CPU,
memory, latency, errors—but traditional tools provide limited ways to export
this information. Locust Telemetry addresses this by using log-based pipelines
to efficiently handle high-volume, distributed metrics. Both master and worker
nodes emit telemetry data, which can be buffered and batched by observability
agents to avoid central bottlenecks.

Currently, telemetry is logged as structured JSON, making it easy to ingest
into modern observability systems. In the future, we are also planning to
support the OpenTelemetry standard for broader observability integration.

By using Locust Telemetry, you can:

- View load testing metrics in your preferred observability tool
- Correlate them with application and infrastructure metrics
- Standardize monitoring across systems without introducing extra dependencies

The plugin is highly extensible—custom metrics and recorders can be added to
monitor scalability and infrastructure behavior under load. We welcome
contributions to expand this project with additional telemetry recorders!


Features
--------

- **Structured Telemetry**
  Captures key events—test lifecycle, request stats, errors, and resource
  warnings—in a structured format suitable for observability pipelines.

- **Master & Worker Metrics**
  Master nodes aggregate overall stats and errors; worker nodes report
  node-specific metrics, including CPU usage.

- **Modular & Extensible**
  Easily add custom recorders (e.g., Kubernetes metrics) and support multiple
  recorders in a single Locust run.

- **Observability Integration**
  Compatible with any log-based or structured telemetry tool, enabling
  flexible dashboards and analysis.

- **Distributed Support**
  Fully compatible with Locust’s master–worker architecture.

- **Flexible Configuration**
  Configurable via CLI arguments or environment variables for easy setup.


Authors
--------------------------------

- Swaroop Shubhakrishna Bhat (`@ss-bhat <https://github.com/ss-bhat>`_)

Many thanks to our other great `contributors! <https://github.com/platform-crew/locust-telemetry/graphs/contributors>`_

License
-------

Locust Telemetry Plugin is licensed under the **Apache License 2.0**.

This license allows you to:

- **Use, reproduce, and distribute** the software in source or binary form.
- **Create derivative works** while including proper notices of changes.
- **Submit contributions**, which are also licensed under Apache 2.0.
- **Benefit from a patent grant** for contributions by each contributor.
- **Use the software "AS IS"** without warranties or guarantees.


For full license text and details, see the `LICENSE <https://github.com/platform-crew/locust-telemetry/blob/main/LICENSE>`_ on GitHub.
