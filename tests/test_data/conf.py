# pylint: disable=invalid-name,redefined-builtin

"""Configuration for sphinx."""

from __future__ import annotations

# -- Project information -----------------------------------------------------
project = "Integration Test Documentation"
release = "1.0.0"
version = "1.0.0"

# -- General configuration ---------------------------------------------------

extensions = ["swagger_plugin_for_sphinx"]
html_static_path = ["_static"]

# -- Swagger -------------------------------------------------

swagger = [
    {
        "name": "OpenAPI Specification",
        "page": "openapi",
        "options": {"url": "../_static/openapi.yml"},
    }
]
