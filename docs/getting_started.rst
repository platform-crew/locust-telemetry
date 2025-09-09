What is Locust Telemetry?
================================

Locust Telemetry is a modular plugin for `Locust <https://docs.locust.io/en/stable/>`_ that provides structured
observability for Locust-based load tests. It enables developers and SREs to
capture rich telemetry data from logs, offering detailed insights into
application performance through your existing observability infrastructure.
Fully compatible with distributed systems following the master-slave model,
both master and slave nodes emit periodic JSON-formatted logs, which can be
easily ingested by any observability tool.

Additionally, Locust Telemetry can be extended to include custom metrics,
such as Kubernetes metrics, allowing you to analyze system scalability and
gain deeper insights into your infrastructure’s behavior under load.

We welcome contributions—please feel free to help expand this project with
additional telemetry plugins!

Motivation
-------------------------

Load testing is essential for understanding how an application or system
behaves under load. Most load-testing tools come with their own dashboards,
which makes it hard to integrate results with your existing observability stack.

In practice, we often need to correlate load test metrics with other
application or infrastructure metrics (CPU, memory, errors, latency, etc.).
Many teams rely on centralized observability platforms like Grafana, Loki,
ELK, or Datadog, but traditional load testing tools provide limited ways to
push data into these ecosystems.

**Locust Telemetry** addresses this by leveraging log-based pipelines to
handle high-volume, distributed load testing data efficiently. Metrics from
multiple places are buffered and batched by observability agents, avoiding
central database bottlenecks and expensive scaling. This scalable approach
integrates load testing into the broader observability tools
in modern organizations.

By emitting all load test metrics as structured JSON logs, Locust
Telemetry enables you to:

- View load testing metrics directly in your preferred observability tool
- Correlate them with application and infrastructure metrics for deeper insights
- Standardize logging and monitoring across systems without extra dependencies



Features
--------

- **Structured Telemetry Logging**
   Captures key events—test start/stop, user spawn completion, request stats, and errors—
   in structured JSON format, ready for monitoring and analytics pipelines.

- **Master Node Recorders**
   Aggregates request statistics, error reports, and lifecycle events on the master node,
   providing periodic updates and final test summaries.

- **Worker Node Recorders**
   Monitors worker-specific metrics, including CPU usage warnings, and logs them as structured events.

- **Plugin Architecture**
   Supports multiple custom telemetry plugins within a single Locust run, making it easy
   to extend with additional metrics sources like Kubernetes.

- **Observability Integration**
   Log-based telemetry works with any observability tool, enabling fully customizable dashboards.

- **Distributed System Support**
   Designed to work seamlessly in distributed Locust setups (master-slave model).

- **CLI & Configuration Support**
   Provides command-line arguments and environment variable configurations for flexible
   runtime setup and plugin configuration.

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
