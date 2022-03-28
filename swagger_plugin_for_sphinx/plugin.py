"""Sphinx Swagger Plugin."""

from __future__ import annotations

import urllib.request
from os.path import abspath, dirname, join
from typing import Any, Iterator

import jinja2
from sphinx.application import Sphinx

import swagger_plugin_for_sphinx

_HERE = abspath(dirname(__file__))


def render(app: Sphinx) -> Iterator[tuple[Any, ...]]:
    """Render the swagger HTML pages."""
    for context in app.config.swagger:
        template_path = join(_HERE, "swagger.j2")

        with open(template_path, encoding="utf-8") as handle:
            template = jinja2.Template(handle.read())

        context.setdefault("options", {})
        context["css_uri"] = app.config.swagger_css_uri
        context["bundle_uri"] = app.config.swagger_bundle_uri
        context["present_uri"] = app.config.swagger_present_uri

        yield context["page"], context, template


def assets(app: Sphinx, exception: BaseException | None) -> None:
    """Move the needed swagger file into the _static folder."""
    if exception:
        return
    if not app.builder:
        return

    urllib.request.urlretrieve(
        app.config.swagger_present_uri,
        join(app.builder.outdir, "_static", "swagger-ui-standalone-preset.js"),
    )
    urllib.request.urlretrieve(
        app.config.swagger_bundle_uri,
        join(app.builder.outdir, "_static", "swagger-ui-bundle.js"),
    )
    urllib.request.urlretrieve(
        app.config.swagger_css_uri,
        join(app.builder.outdir, "_static", "swagger-ui.css"),
    )


def setup(app: Sphinx) -> dict[str, Any]:
    """Setup this plugin."""
    app.add_config_value("swagger", [], "html")
    app.add_config_value(
        "swagger_present_uri",
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-standalone-preset.js",
        "html",
    )
    app.add_config_value(
        "swagger_bundle_uri",
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-bundle.js",
        "html",
    )
    app.add_config_value(
        "swagger_css_uri",
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui.css",
        "html",
    )

    app.connect("html-collect-pages", render)
    app.connect("build-finished", assets)

    return {
        "version": swagger_plugin_for_sphinx.__version__,
        "parallel_read_safe": True,
    }
