# Locust Telemetry


![Tests](https://github.com/platform-crew/locust-telemetry/actions/workflows/tests.yaml/badge.svg)
[![Release](https://img.shields.io/github/v/release/platform-crew/locust-telemetry?color=blue&style=flat-square)](https://github.com/platform-crew/locust-telemetry/releases)
[![Contributors](https://img.shields.io/github/contributors/platform-crew/locust-telemetry?color=brightgreen&style=flat-square)](https://github.com/platform-crew/locust-telemetry/graphs/contributors)
[![codecov](https://codecov.io/gh/platform-crew/locust-telemetry/branch/main/graph/badge.svg)](https://codecov.io/gh/platform-crew/locust-telemetry)
[![License](https://img.shields.io/github/license/platform-crew/locust-telemetry?color=orange&style=flat-square)](https://github.com/platform-crew/locust-telemetry/blob/main/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/locust-telemetry/badge/?version=latest)](https://locust-telemetry.readthedocs.io/en/latest/?badge=latest)

Locust Telemetry is a modular observability plugin for the Locust load-testing
framework. It emits structured telemetry for load and performance tests,
making it easy to export, analyze, and correlate test results with system
metrics.

The plugin supports multiple telemetry backends to fit different workflows:

- **JSON log-based telemetry**:
  A lightweight option for capturing structured events and metrics.

- **OpenTelemetry metrics**:
  Native OpenTelemetry integration for exporting load-test metrics to
  OTLP-compatible backends and correlating them with infrastructure data.

📖 Full documentation is available on [Read the Docs](https://locust-telemetry.readthedocs.io/).

## Motivation

Load testing is most effective when request-level metrics can be correlated
with system signals such as CPU, memory, network usage, latency, and errors.
However, traditional load-testing tools provide limited observability and
export options.

Locust Telemetry addresses this gap by emitting structured telemetry that
integrates cleanly with modern observability stacks, enabling a unified view
of system behavior under load.

## Key Features

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

---

## Installation & Quick Start
Here is a **clean, concise `## Installation & Quick Start` section in Markdown**, faithfully adapted from your RST and aligned with your new README tone.

You can drop this in directly.

---

## Installation & Quick Start

### Requirements

- Python ≥ 3.10
- locust ≥ 2.37.0
- python-json-logger ≥ 3.3.0

---

### Install

Using **pip**:

```bash
pip install locust-telemetry
````

Using **uv**:

```bash
uv install locust-telemetry
```

Using **poetry**:

```bash
poetry add locust-telemetry
```

Verify the installation:

```bash
pip show locust-telemetry
```

---

### Quick Start

Locust Telemetry extends Locust with telemetry recording while preserving
all existing Locust behavior and configuration.

For general Locust usage, see the
[Locust documentation](https://docs.locust.io/en/stable/).

#### 1. Initialize the plugin

In your Locust test file (e.g. `locustfile.py`):

```python
from locust_telemetry import entrypoint

entrypoint.initialize()
```

#### 2. Run Locust with telemetry enabled

**JSON telemetry recorder**

```bash
locust -f locustfile.py \
  --testplan mytest \
  --enable-telemetry-recorder json
```

**OpenTelemetry metrics recorder**

```bash
locust -f locustfile.py \
  --testplan mytest \
  --enable-telemetry-recorder otel
```

---

### Notes

* CLI options can also be set using environment variables:

  * `LOCUST_TESTPLAN_NAME` → `--testplan`
  * `LOCUST_ENABLE_TELEMETRY_RECORDER` → `--enable-telemetry-recorder`

* For all available configuration options, see the
  [Configuration](https://locust-telemetry.readthedocs.io/en/latest/configuration.html)
  section of the documentation.

* For help getting started with Locust itself, refer to the
  [Locust Quick Start Guide](https://docs.locust.io/en/stable/quickstart.html).

---

### Warning

Locust does not currently support native plugin arguments (`--plugin` or `-p`).
As a result, telemetry plugins must be initialized explicitly in
`locustfile.py`.

---

## Local Example (Docker)

Locust Telemetry provides a complete local example that runs Locust with a
full observability stack using Docker. This is the fastest way to see both
JSON and OpenTelemetry telemetry in action.

**Included services:**

- Locust (master + workers)
- OpenTelemetry Collector
- Prometheus
- Loki & Promtail
- Grafana (preconfigured dashboards)

### Run the example

```bash
git clone https://github.com/platform-crew/locust-telemetry.git
cd locust-telemetry/examples/local
make build && make up
````

This starts Locust in distributed mode and launches all required
observability services.

### Access the UIs

* **Locust Web UI**: [http://localhost:8089](http://localhost:8089)
* **Grafana**: [http://localhost:3000](http://localhost:3000) (anonymous access enabled)

Start a test from the Locust UI and wait ~20 seconds for metrics and logs
to appear in Grafana.

### Supported telemetry

* **JSON telemetry**
  Structured logs emitted by Locust and stored in Loki.
  Ideal for event timelines, request metrics, and debugging.

* **OpenTelemetry telemetry**
  Metrics exported via OTLP, collected by the OpenTelemetry Collector,
  scraped by Prometheus, and visualized in Grafana.

> Traces and spans are not yet supported. Only metrics and events are emitted.

📘 **Full setup details, configuration files, and dashboards are documented here:**
[https://locust-telemetry.readthedocs.io/en/latest/examples.html](https://locust-telemetry.readthedocs.io/en/latest/examples.html)

### Dashboard Preview

**JSON Telemetry (Loki / Grafana Logs)**
Structured logs showing request metrics, lifecycle events, and system signals.

![JSON Telemetry Dashboard](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/json-dashboard1.png)
![JSON Telemetry Dashboard](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/json-dashboard2.png)
![JSON Telemetry Dashboard](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/json-dashboard3.png)
![JSON Telemetry Dashboard](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/json-dashboard4.png)

**OpenTelemetry Metrics (Prometheus / Grafana)**
Request latency histograms, system metrics, and user counts exported via OTLP.

![OpenTelemetry Dashboard](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/otel-dashboard1.png)
![OpenTelemetry Dashboard](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/otel-dashboard2.png)
![OpenTelemetry Dashboard](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/otel-dashboard3.png)
![OpenTelemetry Dashboard](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/otel-dashboard4.png)


## Contributing

First of all, thank you for your interest in contributing! Whether it’s
fixing bugs, improving documentation, or adding new features,
your contributions help make Locust Telemetry better for everyone.

Please refer to the [contributing guidelines](https://locust-telemetry.readthedocs.io/en/latest/contributing.html) to get started.

---

## Authors

- Swaroop Shubhakrishna Bhat ([@ss-bhat](https://github.com/ss-bhat))

Thanks to all [contributors](https://github.com/platform-crew/locust-telemetry/graphs/contributors)!

---

## License

Licensed under the [Apache License 2.0](https://github.com/platform-crew/locust-telemetry/blob/main/LICENSE).

---
