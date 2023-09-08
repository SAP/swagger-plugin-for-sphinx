"""Sphinx Swagger Plugin."""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path
from typing import Any, Iterator

import jinja2
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.misc import Raw
from sphinx.application import Sphinx
from sphinx.errors import SphinxError

_HERE = Path(__file__).parent.resolve()


class InlineSwaggerDirective(Raw):  # type:ignore[misc]
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

    app.add_directive("inline-swagger", InlineSwaggerDirective)

    return {
        "version": version("swagger_plugin_for_sphinx"),
        "parallel_read_safe": True,
    }
