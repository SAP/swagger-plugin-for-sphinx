# pylint: disable=missing-function-docstring,redefined-outer-name,too-many-arguments

"""Tests."""

from __future__ import annotations

import urllib.request
from pathlib import Path
from textwrap import dedent
from typing import Any, Callable

import pytest
from pytest_mock import MockerFixture
from sphinx.application import Sphinx

SphinxRunner = Callable[..., None]


@pytest.fixture
def sphinx_runner(tmp_path: Path) -> SphinxRunner:
    docs = tmp_path / "docs"
    docs.mkdir()
    build = tmp_path / "build"
    build.mkdir()

    def run(
        swagger: list[dict[str, Any]],
        swagger_present_uri: str | None = None,
        swagger_bundle_uri: str | None = None,
        swagger_css_uri: str | None = None,
    ) -> None:
        code = ["extensions = ['swagger_plugin_for_sphinx.plugin']"]
        if swagger:
            code.append(f"swagger = {swagger}")
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
        index.touch()

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


def test(sphinx_runner: SphinxRunner, tmp_path: Path) -> None:

    sphinx_runner(
        swagger=[
            {
                "name": "Service API",
                "page": "openapi",
                "options": {
                    "url": "openapi.yaml",
                },
            }
        ]
    )

    build = tmp_path / "build"
    static = build / "_static"

    assert (static / "swagger-ui.css").is_file()
    assert (static / "swagger-ui-bundle.js").is_file()
    assert (static / "swagger-ui-standalone-preset.js").is_file()

    with open(build / "openapi.html", encoding="utf-8") as file:
        html = file.read()

    base_url = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest"
    expected = dedent(
        f"""<!DOCTYPE html>
<html>
    <head>
        <title>Service API</title>
        <link href="{base_url}/swagger-ui.css" rel="stylesheet" type="text/css"/>
        <meta charset="utf-8"/>
    </head>
    <body>
        <div id="swagger-ui-container"></div>
        <script src="{base_url}/swagger-ui-standalone-preset.js"></script>
        <script src="{base_url}/swagger-ui-bundle.js"></script>
        <script>
            config = {{'url': 'openapi.yaml'}}
            config["dom_id"] = "#swagger-ui-container"
            window.onload = function() {{
                window.ui = SwaggerUIBundle(config);
            }}
        </script>
    </body>
</html>"""
    )

    assert expected == html


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
    mocker: MockerFixture,
    tmp_path: Path,
    sphinx_runner: SphinxRunner,
    present_uri: str | None,
    bundle_uri: str | None,
    css_uri: str | None,
    expected_present_uri: str,
    expected_bundle_uri: str,
    expected_css_uri: str,
) -> None:
    urlretrieve = mocker.patch.object(urllib.request, "urlretrieve")

    sphinx_runner([], present_uri, bundle_uri, css_uri)

    base_path = str(tmp_path) + "/build/_static"
    assert urlretrieve.call_args_list == [
        mocker.call(
            expected_present_uri, f"{base_path}/swagger-ui-standalone-preset.js"
        ),
        mocker.call(expected_bundle_uri, f"{base_path}/swagger-ui-bundle.js"),
        mocker.call(expected_css_uri, f"{base_path}/swagger-ui.css"),
    ]
