"""Sphinx Swagger Plugin."""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path
from typing import Any, Iterator

import jinja2
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.misc import Raw
from sphinx.application import Sphinx
from sphinx.errors import ExtensionError, SphinxError
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
    }
    has_content = False

    def run(self) -> list[nodes.Node]:
        app: Sphinx = self.state.document.settings.env.app

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

        div_id = self.options.get("id", "swagger-ui-container")

        node = nodes.container(ids=[div_id], classes=self.options.get("classes", []))
        self.set_source_info(node)

        if "swagger_plugin" not in self.env.metadata[self.env.docname]:
            self.env.metadata[self.env.docname]["swagger_plugin"] = []

        self.env.metadata[self.env.docname]["swagger_plugin"].append(
            {
                "url_path": url_path,
                "div_id": div_id,
            }
        )
        return [node]


def add_css_js(
    app: Sphinx,
    pagename: str,
    _template: str,
    _context: dict[str, Any],
    _doctree: nodes.document,
) -> None:
    """Add Swagger CSS and JS to pages with swagger-plugin directive."""
    if "swagger_plugin" not in app.env.metadata[pagename]:
        return

    context = {"specs": app.env.metadata[pagename]["swagger_plugin"]}

    with open(_HERE / "plugin_directive.j2", encoding="utf-8") as handle:
        template = jinja2.Template(handle.read())

    content = template.render(context)

    app.add_js_file(app.config.swagger_present_uri)
    app.add_js_file(app.config.swagger_bundle_uri)
    app.add_css_file(app.config.swagger_css_uri)
    app.add_js_file(None, body=content)


class InlineSwaggerDirective(Raw):
    """Directive for inline swagger pages."""

    required_arguments = 0
    option_spec = {"id": directives.unchanged_required}
    has_content = False

    def run(self) -> Any:
        app: Sphinx = self.state.document.settings.env.app
        template_path = _HERE / "swagger.j2"

        # find the right configuration for the page
        for index, context in enumerate(app.config.swagger):
            if context.get("id") == self.options["id"]:
                break
        else:
            raise SphinxError(
                f"Cannot find any swagger configuration with id '{self.options['id']}'"
            )

        # remove the configuration, so that we have no double generation
        app.config.swagger.pop(index)

        with template_path.open(encoding="utf-8") as handle:
            template = jinja2.Template(handle.read())

        context.setdefault("options", {})
        context["css_uri"] = app.config.swagger_css_uri
        context["bundle_uri"] = app.config.swagger_bundle_uri
        context["present_uri"] = app.config.swagger_present_uri

        static_folder = Path(app.builder.outdir) / "_static"
        static_folder.mkdir(exist_ok=True)
        content = template.render(context)

        html_file = static_folder / (context["id"] + ".html")
        html_file.write_text(content)

        self.arguments = ["html"]
        self.options["file"] = str(html_file)
        return super().run()


def render(app: Sphinx) -> Iterator[tuple[Any, ...]]:
    """Render the swagger HTML pages."""
    for context in app.config.swagger:
        template_path = _HERE / "swagger.j2"

        with template_path.open(encoding="utf-8") as handle:
            template = jinja2.Template(handle.read())

        context.setdefault("options", {})
        context["css_uri"] = app.config.swagger_css_uri
        context["bundle_uri"] = app.config.swagger_bundle_uri
        context["present_uri"] = app.config.swagger_present_uri

        yield context["page"], context, template


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
    app.connect("html-page-context", add_css_js)

    app.add_directive("inline-swagger", InlineSwaggerDirective)
    app.add_directive("swagger-plugin", SwaggerPluginDirective)

    return {
        "version": version("swagger_plugin_for_sphinx"),
        "parallel_read_safe": True,
    }
