# pylint: disable=redefined-outer-name
"""Integration tests."""

from __future__ import annotations

import subprocess
import time
from contextlib import ExitStack
from pathlib import Path
from typing import Callable, Iterable, Iterator

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


@pytest.fixture
def build_dir(tmp_path: Path) -> str:
    """Return the build directory."""
    return str(tmp_path / "_build")


HostBrowser = Callable[[str, Iterable[str]], webdriver.Remote]


@pytest.fixture(name="host_browser")
def build_and_host_docs(build_dir: str) -> Iterator[HostBrowser]:
    """Build and host the documentation."""
    exit_stack = ExitStack()
    popen: subprocess.Popen[bytes] | None = None

    def _inner(source_dir: str, sphinx_options: Iterable[str]) -> webdriver.Remote:
        nonlocal popen

        subprocess.run(
            ["sphinx-build", *sphinx_options, source_dir, build_dir], check=True
        )

        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")

        browser = exit_stack.enter_context(
            webdriver.Remote("http://localhost:4444", options=options)
        )
        popen = exit_stack.enter_context(
            subprocess.Popen(["python", "-m", "http.server", "--directory", build_dir])
        )
        time.sleep(5)
        return browser  # type: ignore[no-any-return]

    yield _inner

    if popen:
        popen.terminate()
    exit_stack.close()


@pytest.mark.integration
def test_basic(host_browser: HostBrowser) -> None:
    """Test a basic scenario."""
    browser = host_browser("tests/test_data", [])
    _check_page_title(browser, "openapi", ["Swagger Petstore in Main"])
    _check_page_title(
        browser,
        "subfolder/p1",
        ["Swagger Petstore in Subfolder", "Swagger Petstore in Main"],
    )
    _check_page_title(browser, "subfolder/p2", ["Swagger Petstore in Specs"])


@pytest.mark.integration
@pytest.mark.parametrize(
    "builder,openapipage,petspage,rockspage",
    [
        ("html", "openapi", "stores/petstore", "stores/rockstore/rockstore"),
        (
            "dirhtml",
            "openapi/index",
            "stores/petstore/index",
            "stores/rockstore/rockstore/index",
        ),
    ],
)
def test_extension(
    builder: str,
    openapipage: str,
    petspage: str,
    rockspage: str,
    host_browser: HostBrowser,
) -> None:
    """Test referencing specifications from a variety of directories."""
    browser = host_browser("tests/test_subdirs", ["-b", builder])

    _check_page_title(browser, openapipage, ["Swagger Petstore in Main"])
    _check_page_title(
        browser,
        petspage,
        ["Swagger Petstore in Specs", "Swagger Petstore in Samedir"],
    )
    _check_page_title(
        browser,
        rockspage,
        ["Swagger Rockstore in Specs", "Swagger Petstore in Childdir"],
    )


@pytest.mark.integration
def test_dirhtml(host_browser: HostBrowser) -> None:
    """Test a dirhtml scenario."""
    browser = host_browser("tests/test_data", ["-b", "dirhtml"])

    _check_page_title_dirhtml(browser, "openapi", ["Swagger Petstore in Main"])
    _check_page_title_dirhtml(
        browser,
        "subfolder/p1",
        ["Swagger Petstore in Subfolder", "Swagger Petstore in Main"],
    )
    _check_page_title_dirhtml(browser, "subfolder/p2", ["Swagger Petstore in Specs"])


def _check_page_title(
    browser: webdriver.Remote, page: str, expected_title: list[str]
) -> None:
    browser.get(f"http://localhost:8000/{page}.html")
    elements = browser.find_elements(By.CLASS_NAME, "title")
    titles = [element.text.split("\n")[0] for element in elements]
    assert titles == expected_title


def _check_page_title_dirhtml(
    browser: webdriver.Remote, page: str, expected_title: list[str]
) -> None:
    print(page)
    browser.get(f"http://localhost:8000/{page}/")
    elements = browser.find_elements(By.CLASS_NAME, "title")
    titles = [element.text.split("\n")[0] for element in elements]
    assert titles == expected_title
