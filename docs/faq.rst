FAQ
===

**Q: Do I need to change my Locust tests?**
   Minimal changes. You only need to initialize the telemetry plugin once in
   ``locustfile.py``.

**Q: Which telemetry recorders are supported?**
   - **JSON Telemetry Recorder** — structured logs (Loki, ELK, Datadog)
   - **OpenTelemetry Metrics Recorder** — metrics via OTLP (Prometheus, Grafana)

**Q: Can I enable multiple recorders at once?**
   Not currently. Only one recorder (JSON or OpenTelemetry) can be enabled per run.

**Q: Where is telemetry data stored?**
   - JSON telemetry is emitted to stdout and handled by your log backend.
   - OpenTelemetry metrics are exported via OTLP to your metrics backend.

**Q: Can I customize emitted metrics or attributes?**
   Yes. Both recorders support adding custom attributes.

**Q: Are traces and spans supported?**
   Not yet. Only metrics and lifecycle events are emitted.

**Q: How long is telemetry data retained?**
   Retention is controlled by your observability backend, not by Locust Telemetry.
