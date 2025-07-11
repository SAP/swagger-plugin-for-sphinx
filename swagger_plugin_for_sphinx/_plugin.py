"""Sphinx Swagger Plugin."""

from __future__ import annotations

import json
from collections.abc import Iterator
from importlib.metadata import version
from pathlib import Path
from typing import Any

import jinja2
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.errors import ExtensionError
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from sphinx.util.osutil import copyfile, ensuredir
from typing_extensions import override

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

    @override
    def run(self) -> list[nodes.Node]:
        app: Sphinx = self.state.document.settings.env.app
        metadata = self.env.metadata[self.env.docname]
        configs = metadata.setdefault("swagger_plugin", [])
        # The static dir is created by Sphinx and is not available from a variable or function.
        # https://github.com/sphinx-doc/sphinx/blob/v8.1.3/sphinx/builders/html/__init__.py#L897
        static_dir = Path(app.builder.outdir).joinpath("_static")
        path_offset = (
            1
            if app.builder.name == "dirhtml" and app.env.docname.split("/") != ["index"]
            else 0
        )

        if len(self.arguments) != 1:
            raise ExtensionError(
                f"Specify the relative path to the Swagger specification in file: "
                f"{app.env.doc2path(app.env.docname)}:{self.lineno}."
            )

        relpath, abspath = self.env.relfn2path(self.arguments[0])
        # Use dot-dot to address referencing specs from parents of the Sphinx source directory.
        # Otherwise, the spec is copied to a parent of the output directory.
        relpath = relpath.replace("..", "dot-dot")
        spec = Path(abspath).resolve()
        if not spec.exists():
            raise ExtensionError(
                f"In file '{app.env.doc2path(app.env.docname)}:{self.lineno}', "
                f"file not found: {self.arguments[0]}."
            )

        logger.info("Adding to _static output path: %s.", spec)

        # Preserve the source directory structure to avoid name collisions.
        outfile = static_dir.joinpath(relpath)
        ensuredir(str(outfile.parent))
        copyfile(str(spec), str(outfile))

        # The range - 1 is to skip the RST or MD document itself.
        url_path = (
            "".join(
                [
                    "../"
                    for _ in range(len(app.env.docname.split("/")) - 1 + path_offset)
                ]
            )
            + "_static/"
            + relpath
        )

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

        params = {
            "options": config["swagger_options"],
            "css_uri": app.config.swagger_css_uri,
            "bundle_uri": app.config.swagger_bundle_uri,
            "present_uri": app.config.swagger_present_uri,
            "page_title": config["page_title"],
            "url_path": config["url_path"],
        }

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
