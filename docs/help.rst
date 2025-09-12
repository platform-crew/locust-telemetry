.. _help:

OpenTelemetry Support (Help Wanted)
================================
We are actively working on adding **OpenTelemetry support** to `locust-telemetry` and
would love community contributions. The goal is to provide:

- Structured metrics and events compatible with Prometheus, Grafana, and Tempo
- Distributed correlation across Locust master, workers, and Kubernetes clusters
- Tracing of requests and system events for advanced observability

With OpenTelemetry, users will be able to:

- Aggregate metrics across multiple workers automatically
- Monitor system usage and request performance in real-time
- Correlate load tests with infrastructure metrics and distributed services

Help Needed
-----------
We need help from the community to build and improve OpenTelemetry support.
Specifically, contributions are welcome in the following areas:

- Implementing Master and Worker OpenTelemetry recorders
- Adding Kubernetes/OpenTelemetry recorder support
- Creating Grafana dashboard examples for OpenTelemetry metrics
- Testing and providing feedback on distributed tracing and metrics aggregation

If you are interested in contributing, please see the :ref:`contributing`
