Frequently Asked Questions
================================

**Q: Do I need to modify my Locust tests to use Locust Telemetry?**
    No. You only need to load the telemetry at the start of your test script.

**Q: Can I use multiple telemetry recorders together?**
    Yes. Locust Telemetry is designed to support multiple recorder plugins in a single run.
    However, at the moment, only one recorder plugin is available within locust-telemetry.

**Q: Where are telemetry logs stored?**
    By default, logs are printed to **stdout** in a structured **JSON format**.
    You can then use a log aggregator or any observability tool of your choice to visualize the metrics.
    Please, see the :ref:`examples-section`.

**Q: Can I customize the metrics that are logged?**
    Yes. The plugin provides a method that can be used to add additional attributes.

**Q: How long are logs retained?**
    The plugin only emits structured JSON metric logs (not raw application logs).
    Retention depends on your log storage system (Grafana Loki, ELK, Datadog, etc.).
