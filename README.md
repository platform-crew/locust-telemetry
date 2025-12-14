# Locust Telemetry

![Tests](https://github.com/platform-crew/locust-telemetry/actions/workflows/tests.yaml/badge.svg)
[![Release](https://img.shields.io/github/v/release/platform-crew/locust-telemetry)](https://github.com/platform-crew/locust-telemetry/releases)
[![codecov](https://codecov.io/gh/platform-crew/locust-telemetry/branch/main/graph/badge.svg)](https://codecov.io/gh/platform-crew/locust-telemetry)
[![License](https://img.shields.io/github/license/platform-crew/locust-telemetry)](LICENSE)
[![Docs](https://readthedocs.org/projects/locust-telemetry/badge/?version=latest)](https://locust-telemetry.readthedocs.io/en/stable/)

**Locust Telemetry** is a modular observability plugin for the
[Locust](https://locust.io) load-testing framework.

It emits structured telemetry from load tests so you can **correlate
request behavior with system metrics** using modern observability tools.

📖 **Full documentation:**
https://locust-telemetry.readthedocs.io/en/stable/index.html

---

## Why Locust Telemetry?

Load testing is most effective when request-level metrics can be correlated
with system signals like CPU, memory, network usage, and errors.

Locust Telemetry bridges this gap by exporting structured telemetry that
integrates cleanly with existing observability stacks.

---

## Key Features

- **Structured Telemetry**
  Test lifecycle events, request metrics, and system metrics

- **Multiple Backends**
  JSON logs or OpenTelemetry metrics

- **OpenTelemetry Native**
  OTLP export to Prometheus, Grafana, Datadog, New Relic, and more

- **Distributed Support**
  Works with Locust master–worker mode

- **Extensible Design**
  Add custom recorders and instruments

> Traces and spans are planned but not yet supported.

---

## Installation

```bash
pip install locust-telemetry
````

---

## Quick Start

### 1. Initialize the plugin

In your `locustfile.py`:

```python
from locust_telemetry import entrypoint

entrypoint.initialize()
```

### 2. Run Locust with telemetry enabled

**JSON telemetry (logs):**

```bash
locust -f locustfile.py --testplan mytest --enable-telemetry-recorder json
```

**OpenTelemetry metrics:**

```bash
locust -f locustfile.py --testplan mytest --enable-telemetry-recorder otel
```

➡️ See the **Configuration** section in the docs for all available options.

---

## Local Demo (Docker)

A complete local observability stack is provided to quickly try both
JSON and OpenTelemetry telemetry:

```bash
git clone https://github.com/platform-crew/locust-telemetry.git
cd locust-telemetry/examples/local
make build && make up
```

* Locust UI: [http://localhost:8089](http://localhost:8089)
* Grafana: [http://localhost:3000](http://localhost:3000)

📘 Full walkthrough:
[https://locust-telemetry.readthedocs.io/en/stable/examples.html](https://locust-telemetry.readthedocs.io/en/latest/examples.html)

---

## Dashboard Preview

**JSON Telemetry (Loki / Grafana Logs)**
![JSON Dashboard](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/json-dashboard1.png)
![JSON Dashboard](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/json-dashboard4.png)

**OpenTelemetry Metrics (Prometheus / Grafana)**
![OTel Dashboard](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/otel-dashboard1.png)
![OTel Dashboard](https://raw.githubusercontent.com/platform-crew/locust-telemetry/main/docs/_static/otel-dashboard4.png)

---

## Contributing

Contributions are welcome!
Please see [contributing](https://locust-telemetry.readthedocs.io/en/stable/contributing.html) for guidelines.

---

## Author

**Swaroop Shubhakrishna Bhat** ([@ss-bhat](https://github.com/ss-bhat))

Thanks to all contributors ❤️

---

## License

Licensed under the Apache License 2.0.
See [LICENSE](LICENSE) for details.
