"""Sphinx Swagger Plugin."""

from __future__ import annotations

import json
from importlib.metadata import version
from pathlib import Path
from typing import Any, Iterator

import jinja2
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.errors import ExtensionError
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

logger = logging.getLogger(__name__)
_HERE = Path(__file__).parent.resolve()


class SwaggerPluginDirective(SphinxDirective):
    """Directive for Swagger content."""

    required_arguments = 0
    # Required arg, path to the specification, is marked as optional
    # so the directive can throw the exception rather than docutils.
    optional_arguments = 1
    option_spec = {
        "id": directives.unchanged,
        "classes": directives.class_option,
        "full-page": directives.flag,
        "page-title": directives.unchanged,
        "swagger-options": directives.unchanged,
    }
    has_content = False

    def run(self) -> list[nodes.Node]:
        app: Sphinx = self.state.document.settings.env.app
        metadata = self.env.metadata[self.env.docname]
        configs = metadata.setdefault("swagger_plugin", [])

        if len(self.arguments) != 1:
            raise ExtensionError(
                f"Specify the relative path to the Swagger specification in file: "
                f"{app.env.doc2path(app.env.docname)}:{self.lineno}."
            )

        relpath, abspath = self.env.relfn2path(self.arguments[0])
        spec = Path(abspath).resolve()
        if not spec.exists():
            raise ExtensionError(
                f"In file '{app.env.doc2path(app.env.docname)}:{self.lineno}', "
                f"file not found: {self.arguments[0]}."
            )

        rel_parts = Path(relpath).parts
        static = Path(app.srcdir).joinpath(rel_parts[0])
        logger.info(f"Adding to html_static_path: {static}.")
        app.config.html_static_path.extend([static])

        # If the relative path does not start with _static/, add it.
        url_path = self.arguments[0]
        if not url_path.startswith("_static/"):
            url_path = "_static/" + url_path

        config = {
            "full_page": "full-page" in self.options,
            "url_path": url_path,
            "swagger_options": json.loads(self.options.get("swagger-options", "{}")),
            "page_title": self.options.get("page-title", "OpenAPI Specification"),
        }
        configs.append(config)

        if config["full_page"]:
            return []

        div_id = self.options.get("id", "swagger-ui-container")
        node = nodes.container(ids=[div_id], classes=self.options.get("classes", []))
        self.set_source_info(node)
        config["div_id"] = div_id
        return [node]


def add_css_js(
    app: Sphinx,
    pagename: str,
    _template: str,
    _context: dict[str, Any],
    _doctree: nodes.document,
) -> None:
    """Add Swagger CSS and JS to pages with swagger-plugin directive."""
    configs = app.env.metadata[pagename].get("swagger_plugin", [])

    if not configs:
        return
    if configs[0]["full_page"]:
        return

    with open(_HERE / "inline_template.j2", encoding="utf-8") as handle:
        template = jinja2.Template(handle.read())

    content = template.render({"specs": configs})

    app.add_js_file(app.config.swagger_present_uri)
    app.add_js_file(app.config.swagger_bundle_uri)
    app.add_css_file(app.config.swagger_css_uri)
    app.add_js_file(None, body=content)


def render(app: Sphinx) -> Iterator[tuple[Any, ...]]:
    """Render the swagger HTML pages."""
    for pagename, context in app.env.metadata.items():
        configs = context.get("swagger_plugin", [])
        if not configs:
            continue
        config = configs[0]
        if not config["full_page"]:
            continue

        template_path = _HERE / "full_page_template.j2"
        with template_path.open(encoding="utf-8") as handle:
            template = jinja2.Template(handle.read())

        params = {}
        params["options"] = config["swagger_options"]
        params["css_uri"] = app.config.swagger_css_uri
        params["bundle_uri"] = app.config.swagger_bundle_uri
        params["present_uri"] = app.config.swagger_present_uri
        params["page_title"] = config["page_title"]
        params["url_path"] = config["url_path"]

        yield pagename, params, template


def setup(app: Sphinx) -> dict[str, Any]:
    """Setup this plugin."""
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
    app.connect("html-page-context", add_css_js)

    app.add_directive("swagger-plugin", SwaggerPluginDirective)

    return {
        "version": version("swagger_plugin_for_sphinx"),
        "parallel_read_safe": True,
    }
