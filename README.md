# Locust Telemetry

![Tests](https://github.com/platform-crew/locust-telemetry/actions/workflows/tests.yaml/badge.svg)
[![Release](https://img.shields.io/github/v/release/platform-crew/locust-telemetry?color=blue&style=flat-square)](https://github.com/platform-crew/locust-telemetry/releases)
[![Contributors](https://img.shields.io/github/contributors/platform-crew/locust-telemetry?color=brightgreen&style=flat-square)](https://github.com/platform-crew/locust-telemetry/graphs/contributors)
[![codecov](https://codecov.io/gh/platform-crew/locust-telemetry/branch/main/graph/badge.svg)](https://codecov.io/gh/platform-crew/locust-telemetry)
[![License](https://img.shields.io/github/license/platform-crew/locust-telemetry?color=orange&style=flat-square)](https://github.com/platform-crew/locust-telemetry/blob/main/LICENSE)

# Locust Telemetry

**Locust Telemetry** is a modular plugin for [Locust](https://docs.locust.io/en/stable/)
that provides **structured observability** for load tests. Both master and
worker nodes emit **JSON-formatted logs**, which can be ingested by any
observability tool, including Grafana, ELK, Loki, or Datadog.

It can also be extended to include custom metrics (e.g., Kubernetes), helping
you analyze system performance and scalability under load.

---

## Key Features

- **Structured Logging**: Logs test start/stop, user spawn, request stats, and errors in JSON.
- **Master & Worker Recorders**: Aggregates metrics on the master; monitors CPU/memory on workers.
- **Plugin Architecture**: Easily extend with custom telemetry plugins.
- **Distributed System Support**: Works seamlessly in master-slave Locust setups.
- **CLI & Configurable**: Configure via command-line arguments or environment variables.

---

## Motivation

Load testing is crucial to understanding how applications and systems behave under stress. Most load-testing tools provide their own dashboards, which makes it difficult to integrate results with existing observability stacks.

**Locust Telemetry** solves this problem by emitting structured, JSON-formatted logs for all test metrics. These logs can be ingested by any observability tool—Grafana, Loki, ELK, Datadog, or others—allowing you to:

- Visualize load test metrics directly in your preferred observability platform.
- Correlate load test data with application and infrastructure metrics (CPU, memory, latency, errors) for deeper insights.
- Standardize monitoring and logging across systems without introducing additional dependencies.

By leveraging log-based pipelines, Locust Telemetry handles high-volume, distributed load testing efficiently and integrates seamlessly with modern observability workflows.

---

## Installation & Quick Start

### Requirements

- Python 3.9+
- locust >= 2.37.0
- python-json-logger >= 3.3.0

### Install via pip

```bash
pip install locust-telemetry
pip show locust-telemetry  # validate installation
````

### Load the core telemetry plugin

Add the following to your `locustfile.py`:

```python
from locust_telemetry.core_telemetry.plugin import entry_point
entry_point()
```

### Run your first test

Please refer to the official [Locust Quick Start Guide](https://docs.locust.io/en/stable/quickstart.html).

### Notes

* Telemetry plugins are singletons; loading a plugin multiple times will **not** generate duplicate events.
* Locust currently does **not** support CLI plugin arguments (`--plugin` or `-p`), so plugins must be loaded manually in `locustfile.py`.
* The Locust team is planning to add support for CLI and environment variables in the future. You can track progress here: [Issue #3212](https://github.com/locustio/locust/issues/3212).

---

## Examples - Setting Up Locally

**Locust Telemetry** can be visualized in real time using tools like **Grafana**, **Loki**, and **Promtail**. Once your load tests are running, metrics from both master and worker nodes are emitted as structured JSON logs, which can be ingested by your observability stack.

### Key Features Demonstrated

- **All Load Test Runs**: View a summary of every test run and quickly navigate to detailed dashboards.
- **Request Metrics**: Track request statistics, failures, endpoint performance, and user activity.
- **System Metrics**: Monitor CPU, memory, and other resource usage from both master and worker nodes.
- **Correlation**: Combine load test metrics with your application and infrastructure telemetry for deeper insights.
- **Custom Dashboards**: Fully customizable Grafana dashboards for visualizing metrics in a way that fits your workflow.

### Dashboard Screenshots

Below are sample dashboards showing how Locust Telemetry metrics can be explored:

*Overview of all load test runs*

![All Load Test Runs](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/source/_static/load-test-runs.png)

*Request metrics and performance overview*

![Request Dashboard 1](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/source/_static/request-dashboard-1.png)

*Endpoint-specific statistics*

![Request Dashboard 2](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/source/_static/request-dashboard-2.png)

*Errors and failures visualized*

![Request Dashboard 3](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/source/_static/request-dashboard-3.png)

*System metrics and CPU warnings*

![Request Dashboard 4](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/source/_static/request-dashboard-4.png)


### 🚀 Full Setup Instructions

For complete setup details and examples, refer to the [Read the Docs examples section](https://your-docs-link/examples-section).

---

## Contributing

First of all, thank you for your interest in contributing! Whether it’s
fixing bugs, improving documentation, or adding new features,
your contributions help make Locust Telemetry better for everyone.

Please refer to the [contributing guidelines](CONTRIBUTING.md) to get started.

---

## Authors

- Swaroop Shubhakrishna Bhat ([@ss-bhat](https://github.com/ss-bhat))

Thanks to all [contributors](https://github.com/platform-crew/locust-telemetry/graphs/contributors)!

---

## License

Licensed under the [Apache License 2.0](https://github.com/platform-crew/locust-telemetry/blob/main/LICENSE).

---
