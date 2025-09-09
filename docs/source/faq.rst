Frequently Asked Questions
================================

**Q: Do I need to modify my Locust tests to use Locust Telemetry?**
    No. You only need to load the plugin at the start of your test script.

**Q: Can I use multiple telemetry plugins together?**
    Yes. Locust Telemetry is designed to support multiple plugins in a single run.
    However, at the moment, only one plugin is available within telemetry.

**Q: Where are telemetry logs stored?**
    Logs are printed to **stdout** by default in a structured **JSON format**.

**Q: Can I customize the metrics that are logged?**
    Yes. The plugin provides a method that can be used to add additional attributes.
