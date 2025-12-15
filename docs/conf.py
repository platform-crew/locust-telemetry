# Configuration file for the Sphinx documentation builder.

import os
import sys
from datetime import datetime

# -- Path setup --------------------------------------------------------------

# Add the locust_telemetry package to sys.path
sys.path.insert(0, os.path.abspath("../"))

# -- Project information -----------------------------------------------------

project = "Locust Telemetry"
author = "Swaroop Shubhakrishna Bhat"
copyright = f"{datetime.now().year}, {author}"
release = "v0.1.0"

# -- General configuration ---------------------------------------------------

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",  # Auto-generate docs from docstrings
    "sphinx.ext.napoleon",  # Google/NumPy-style docstrings
    "myst_parser",  # Markdown support with MyST
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.todo",  # Support TODOs in docs
    "sphinx.ext.intersphinx",  # Link to external docs
    "sphinx_rtd_theme",  # Read the Docs theme
    "sphinx.ext.extlinks",  # Shortcuts for external links
    "sphinx_substitution_extensions",  # Reusable text/substitutions
    "sphinx-prompt",  # CLI prompt formatting
]

# Paths that contain templates
templates_path = ["_templates"]

# Patterns to exclude
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- HTML output options -----------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Autodoc settings --------------------------------------------------------

autodoc_member_order = "bysource"
autoclass_content = "both"  # Include class docstring + __init__
autodoc_typehints = "description"

# -- Napoleon settings -------------------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

# -- Intersphinx configuration ----------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "locust": ("https://docs.locust.io/en/stable/", None),
}

# -- extlinks examples -------------------------------------------------------

extlinks = {
    "issue": (
        "https://github.com/platform-crew/locust-observability/issues/%s",
        "issue #",
    ),
    "pr": ("https://github.com/platform-crew/locust-observability/pull/%s", "PR #"),
}

# -- TODO settings -----------------------------------------------------------

todo_include_todos = False

html_title = "Locust Telemetry Documentation"
html_short_title = "Locust Telemetry Plugin"
html_meta = {
    "description": (
        "Locust Telemetry is a plugin for the Locust load-testing framework that "
        "emits structured metrics and telemetry to observability tools like "
        "Prometheus, Grafana, Loki, and Datadog."
    ),
    "keywords": (
        "locust, locust telemetry, load testing, metrics, observability, "
        "json telemetry, opentelemetry, otel, prometheus, grafana, loki, datadog"
    ),
    "viewport": "width=device-width, initial-scale=1",
    "language": "en",
    "robots": "index, follow",
}
