What is Locust Telemetry?
=========================

Locust Telemetry is a modular observability plugin for the Locust load-testing
framework. It emits structured telemetry and metrics, making it easy to export,
analyze, and correlate test results with system performance data.

It supports multiple telemetry backends to fit different workflows:

- **JSON Telemetry** — lightweight structured logs for tools like Loki, ELK,
  or any log-based backend.
- **OpenTelemetry Metrics** — native OTLP metrics for Prometheus, Grafana,
  Datadog, New Relic or any OpenTelemetry-compatible backend.

Motivation
----------

Load testing is most effective when request-level metrics can be correlated
with system signals such as CPU, memory, network usage, latency, and errors.
Traditional load-testing tools often provide limited observability.

Locust Telemetry fills this gap by integrating seamlessly with modern
observability stacks, providing a unified view of system behavior under load.


Features
----------

- **Structured Telemetry**
  Emits test lifecycle events, request metrics, and system usage in JSON or
  OpenTelemetry formats.

- **OpenTelemetry Integration**
  Exports metrics via OTLP for correlation with existing observability data.

- **Distributed Support**
  Compatible with Locust’s master–worker architecture.

- **Modular & Extensible**
  Easily extended with custom recorders.

- **Traces & Spans (Coming Soon)**
  Planned OpenTelemetry trace and span support for end-to-end correlation.


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
