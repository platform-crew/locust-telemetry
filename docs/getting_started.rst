What is Locust Telemetry?
==========================

Locust Telemetry is a modular plugin for `Locust <https://docs.locust.io/en/stable/>`_
that provides structured observability for load tests. It captures telemetry
data as JSON logs, enabling seamless integration with existing observability
tools and offering detailed insights into system performance.

Compatible with distributed systems, both master and worker nodes periodically
emit logs that can be easily ingested. This plugin is also extensible—custom
metrics (e.g., Kubernetes metrics) can be added to analyze scalability and
infrastructure behavior under load.

We welcome contributions—please help expand this project with additional
telemetry recorders!

Motivation
----------

Load testing is critical to understand how systems behave under stress, but
most tools rely on proprietary dashboards that don’t integrate well with
existing observability stacks. Teams often need to correlate load test metrics
with infrastructure data (CPU, memory, latency, errors, etc.), but traditional
load testing tools provide limited ways to push data into these ecosystems.

**Locust Telemetry** solves this by leveraging log-based pipelines to handle
high-volume, distributed load testing data efficiently. Metrics from multiple
sources are buffered and batched by observability agents, avoiding central
database bottlenecks and expensive scaling. This approach makes it easy to
integrate load testing into modern observability practices.

By emitting metrics as structured JSON logs, Locust Telemetry enables you to:

- View load testing metrics in your preferred observability tool
- Correlate them with application and infrastructure metrics
- Standardize monitoring across systems without extra dependencies


Features
--------

- **Structured Telemetry**
   Logs key events—test lifecycle, request stats, errors, and resource warnings—
   in JSON format, ready for observability pipelines.

- **Master & Worker Recorders**
   Master aggregates request stats and errors; workers report node-specific metrics,
   including CPU usage.

- **Modular Architecture**
   Easily extend this plugin with custom recorders (e.g., Kubernetes metrics) within a single
   Locust run. Designed to support multiple recorders.

- **Observability Integration**
   Works with any log-based observability tool, enabling customizable dashboards
   and analysis.

- **Distributed Support**
   Fully compatible with Locust’s master–worker model.

- **Flexible Configuration**
   Supports both CLI arguments and environment variables for setup.


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
