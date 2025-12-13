# Locust Telemetry


![Tests](https://github.com/platform-crew/locust-telemetry/actions/workflows/tests.yaml/badge.svg)
[![Release](https://img.shields.io/github/v/release/platform-crew/locust-telemetry?color=blue&style=flat-square)](https://github.com/platform-crew/locust-telemetry/releases)
[![Contributors](https://img.shields.io/github/contributors/platform-crew/locust-telemetry?color=brightgreen&style=flat-square)](https://github.com/platform-crew/locust-telemetry/graphs/contributors)
[![codecov](https://codecov.io/gh/platform-crew/locust-telemetry/branch/main/graph/badge.svg)](https://codecov.io/gh/platform-crew/locust-telemetry)
[![License](https://img.shields.io/github/license/platform-crew/locust-telemetry?color=orange&style=flat-square)](https://github.com/platform-crew/locust-telemetry/blob/main/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/locust-telemetry/badge/?version=latest)](https://locust-telemetry.readthedocs.io/en/latest/?badge=latest)

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

📖 Full documentation is available on [Read the Docs](https://locust-telemetry.readthedocs.io/).

## Key Features

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

This extension enhances Locust with telemetry recording while preserving all existing Locust usage patterns and configuration options.
For details on Locust itself, refer to the official [Locust documentation](https://docs.locust.io/en/stable/index.html).

---

#### 1. Initialize the telemetry plugin

In your Locust test script (e.g., `locustfile.py`):

```python
from locust_telemetry import entrypoint
entrypoint.initialize()
````

---

#### 2. Run your Locust tests

Run with telemetry enabled. Specify the test plan and the recorder plugin:

```bash
$ locust -f locustfile.py --testplan mytest --enable-telemetry-recorder json
```

##### Note

* CLI arguments can also be configured via environment variables:

  * `LOCUST_TESTPLAN_NAME` → equivalent to `--testplan`
  * `LOCUST_ENABLE_TELEMETRY_RECORDER` → equivalent to `--enable-telemetry-recorder`
* For a complete list of telemetry configuration options, see the [configuration section](https://locust-telemetry.readthedocs.io/en/latest/configuration.html).
* For guidance on setting up Locust tests, consult the [Locust Quick Start Guide](https://docs.locust.io/en/stable/quickstart.html).

##### Warning

* Locust currently does not support plugin arguments (`--plugin` or `-p`). Therefore, plugins must be loaded manually in `locustfile.py`.
* The Locust team is planning to add native support for CLI and environment variables for plugins, which will allow direct plugin specification in the run command. Track progress in issue [#3212](https://github.com/locustio/locust/issues/3212).

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
