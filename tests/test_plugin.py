# pylint: disable=missing-function-docstring,redefined-outer-name,too-many-arguments

"""Tests."""

from __future__ import annotations

import shutil
from pathlib import Path
from textwrap import dedent
from typing import Callable

import pytest
from sphinx.application import Sphinx
from sphinx.errors import ExtensionError

SphinxRunner = Callable[..., None]


@pytest.fixture
def sphinx_runner(tmp_path: Path) -> SphinxRunner:
    docs = tmp_path / "docs"
    docs.mkdir()
    build = tmp_path / "build"
    build.mkdir()

    def run(
        directive: str,
        swagger_present_uri: str | None = None,
        swagger_bundle_uri: str | None = None,
        swagger_css_uri: str | None = None,
    ) -> None:
        code = ["extensions = ['swagger_plugin_for_sphinx']"]
        if swagger_present_uri:
            code.append(f"swagger_present_uri = '{swagger_present_uri}'")
        if swagger_bundle_uri:
            code.append(f"swagger_bundle_uri = '{swagger_bundle_uri}'")
        if swagger_css_uri:
            code.append(f"swagger_css_uri = '{swagger_css_uri}'")

        conf = docs / "conf.py"
        with open(conf, "w+", encoding="utf-8") as file:
            file.write("\n".join(code))

        index = docs / "index.rst"
        index.write_text(
            "Project\n=======\n\n.. toctree::\n   api.rst",
            encoding="utf-8",
        )
        api = docs / "api.rst"
        api.write_text(
            f"API\n===\n\n{directive}\n",
            encoding="utf-8",
        )

        spec = Path(__file__).parent / "test_data" / "openapi.yml"
        shutil.copyfile(str(spec), str(docs / "openapi.yaml"))
        shutil.copyfile(str(spec), str(docs / "other.yaml"))

        Sphinx(
            srcdir=str(docs),
            confdir=str(docs),
            outdir=str(build),
            doctreedir=str(build / ".doctrees"),
            buildername="html",
        ).build()

    return run


def test_run_empty(sphinx_runner: SphinxRunner) -> None:
    sphinx_runner([])


def test_full_page(sphinx_runner: SphinxRunner, tmp_path: Path) -> None:
    sphinx_runner(
        directive=".. swagger-plugin:: openapi.yaml\n   :full-page:",
    )

    build = tmp_path / "build"
    with open(build / "api.html", encoding="utf-8") as file:
        html = file.read()

    base_url = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest"
    expected = dedent(
        f"""<!DOCTYPE html>
<html>
    <head>
        <title>OpenAPI Specification</title>
        <link href="{base_url}/swagger-ui.css" rel="stylesheet" type="text/css"/>
        <meta charset="utf-8"/>
    </head>
    <body>
        <div id="swagger-ui-container"></div>
        <script src="{base_url}/swagger-ui-standalone-preset.js"></script>
        <script src="{base_url}/swagger-ui-bundle.js"></script>
        <script>
            config = {{}}
            config["dom_id"] = "#swagger-ui-container"
            config["url"] = "_static/openapi.yaml"
            window.onload = function() {{
                window.ui = SwaggerUIBundle(config);
            }}
        </script>
    </body>
</html>"""
    )

    assert expected == html


def test_inline(sphinx_runner: SphinxRunner, tmp_path: Path) -> None:
    contents = dedent(
        """
    API
    ===

    .. swagger-plugin:: openapi.yaml
       :id: one

    .. swagger-plugin:: other.yaml
       :id: two
    """
    )
    sphinx_runner(directive=contents)

    build = tmp_path / "build"
    with open(build / "api.html", encoding="utf-8") as file:
        html = file.read()

    assert "sphinx" in html
    assert "https://cdn.jsdelivr.net" in html
    assert "_static/openapi.yaml" in html
    assert "#one" in html
    assert "_static/other.yaml" in html
    assert "#two" in html
    assert html.count("window.ui = SwaggerUIBundle({") == 2
    assert html.count("swagger-ui-bundle.js") == 1

    assert (tmp_path / "build" / "_static" / "openapi.yaml").exists()
    assert (tmp_path / "build" / "_static" / "other.yaml").exists()


def test_swagger_plugin_directive_same_dir(
    sphinx_runner: SphinxRunner, tmp_path: Path
) -> None:
    sphinx_runner(".. swagger-plugin:: openapi.yaml")

    build = tmp_path / "build"
    with open(build / "api.html", encoding="utf-8") as file:
        html = file.read()

    assert "_static/openapi.yaml" in html
    assert "#swagger-ui-container" in html

    spec = tmp_path / "build" / "_static" / "openapi.yaml"
    assert spec.exists()


def test_spec_not_found(sphinx_runner: SphinxRunner) -> None:
    with pytest.raises(ExtensionError, match="file not found: unknown"):
        sphinx_runner(directive=".. swagger-plugin:: unknown")


def test_swagger_plugin_directive_no_arg(sphinx_runner: SphinxRunner) -> None:
    with pytest.raises(ExtensionError, match="docs/api.rst:4"):
        sphinx_runner(directive=".. swagger-plugin::\n   :id: pet-store")


@pytest.mark.parametrize(
    "present_uri,bundle_uri,css_uri,expected_present_uri,expected_bundle_uri,expected_css_uri",
    [
        (
            None,
            None,
            None,
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-standalone-preset.js",
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-bundle.js",
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui.css",
        ),
        (
            "foo-present",
            "foo-bundle",
            "foo-css",
            "foo-present",
            "foo-bundle",
            "foo-css",
        ),
    ],
)
def test_custom_urls(
    tmp_path: Path,
    sphinx_runner: SphinxRunner,
    present_uri: str | None,
    bundle_uri: str | None,
    css_uri: str | None,
    expected_present_uri: str,
    expected_bundle_uri: str,
    expected_css_uri: str,
) -> None:
    sphinx_runner(
        ".. swagger-plugin:: openapi.yaml\n   :full-page:",
        present_uri,
        bundle_uri,
        css_uri,
    )

    build = tmp_path / "build"
    with open(build / "api.html", encoding="utf-8") as file:
        html = file.read()

    expected = dedent(
        f"""<!DOCTYPE html>
<html>
    <head>
        <title>OpenAPI Specification</title>
        <link href="{expected_css_uri}" rel="stylesheet" type="text/css"/>
        <meta charset="utf-8"/>
    </head>
    <body>
        <div id="swagger-ui-container"></div>
        <script src="{expected_present_uri}"></script>
        <script src="{expected_bundle_uri}"></script>
        <script>
            config = {{}}
            config["dom_id"] = "#swagger-ui-container"
            config["url"] = "_static/openapi.yaml"
            window.onload = function() {{
                window.ui = SwaggerUIBundle(config);
            }}
        </script>
    </body>
</html>"""
    )

    assert expected == html
