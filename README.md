# Locust Telemetry


![Tests](https://github.com/platform-crew/locust-telemetry/actions/workflows/tests.yaml/badge.svg)
[![Release](https://img.shields.io/github/v/release/platform-crew/locust-telemetry?color=blue&style=flat-square)](https://github.com/platform-crew/locust-telemetry/releases)
[![Contributors](https://img.shields.io/github/contributors/platform-crew/locust-telemetry?color=brightgreen&style=flat-square)](https://github.com/platform-crew/locust-telemetry/graphs/contributors)
[![codecov](https://codecov.io/gh/platform-crew/locust-telemetry/branch/main/graph/badge.svg)](https://codecov.io/gh/platform-crew/locust-telemetry)
[![License](https://img.shields.io/github/license/platform-crew/locust-telemetry?color=orange&style=flat-square)](https://github.com/platform-crew/locust-telemetry/blob/main/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/locust-telemetry/badge/?version=latest)](https://locust-telemetry.readthedocs.io/en/latest/?badge=latest)

**Locust Telemetry Plugin** is an open-source plugin for [Locust](https://docs.locust.io/en/stable/)
that adds telemetry, metrics, and observability to your load tests.

It logs Locust stats and events (requests, failures, users, system metrics) as
structured JSON logs, which can be ingested into Grafana, ELK, Loki, Datadog,
or any observability platform.

The plugin is fully extensible — you can add custom metrics
(e.g., Kubernetes resource usage) to analyze application performance
and scalability under load.

📖 Full documentation is available on [Read the Docs](https://locust-telemetry.readthedocs.io/).

---
## Why Locust Telemetry Plugin?

While Locust is great for load testing, its built-in stats are not always easy to integrate into modern observability platforms.
The **Locust Telemetry Plugin** bridges this gap by exporting all test metrics as JSON logs, making it simple to send data into Grafana, ELK, Loki, Prometheus, or Datadog.

---

## Key Features

- **Structured JSON Logging**: Captures test lifecycle events, request stats, and errors in a machine-readable format.
- **Master & Worker Metrics**: Aggregates stats on the master; monitors CPU and memory usage on workers.
- **Plugin Architecture**: Extend with custom telemetry modules (e.g., Kubernetes metrics).
- **Distributed Load Testing**: Works seamlessly in master–worker Locust setups.
- **Configurable**: Control behavior via CLI arguments or environment variables.

---

## Motivation

Load testing is critical for understanding how applications behave under stress, but most tools lock results into their own dashboards. That makes it hard to integrate with existing **observability stacks** like Grafana, Loki, ELK, or Datadog.

The **Locust Telemetry Plugin** bridges this gap by exporting all Locust test metrics as **structured JSON logs**. This allows you to:

- Visualize load test results in your existing monitoring dashboards
- Correlate test metrics with infrastructure telemetry (CPU, memory, latency, errors)
- Standardize logging across distributed environments without extra dependencies

By using log-based pipelines, Locust Telemetry scales effortlessly and integrates into modern observability workflows.

---

## Installation & Quick Start

### Requirements

- Python >= 3.10
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
from locust_telemetry.recorders.locust import setup_telemetry

setup_telemetry()
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

![All Load Test Runs](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/load-test-runs.png)

*Request metrics and performance overview*

![Request Dashboard 1](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/request-dashboard-1.png)

*Endpoint-specific statistics*

![Request Dashboard 2](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/request-dashboard-2.png)

*Errors and failures visualized*

![Request Dashboard 3](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/request-dashboard-3.png)

*System metrics and CPU warnings*

![Request Dashboard 4](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/request-dashboard-4.png)


### 🚀 Full Setup Instructions

For complete setup details and examples, refer to the [Read the Docs examples section](https://locust-telemetry.readthedocs.io/en/latest/examples.html).

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
