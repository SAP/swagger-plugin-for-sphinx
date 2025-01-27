"""Integration tests."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


@pytest.fixture
def build_dir(tmp_path: Path) -> str:
    """Return the build directory."""
    return str(tmp_path / "_build")


@pytest.mark.integration
def test_basic(build_dir: str) -> None:
    """Test a basic scenario."""
    subprocess.run(["sphinx-build", "tests/test_data", build_dir], check=True)

    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")

    with (
        webdriver.Remote("http://localhost:4444", options=options) as browser,
        subprocess.Popen(
            [
                "python",
                "-m",
                "http.server",
                "--directory",
                build_dir,
            ]
        ) as popen,
    ):
        time.sleep(5)
        try:
            _check_page_title(browser, "openapi", ["Swagger Petstore in Main"])
            _check_page_title(
                browser,
                "subfolder/p1",
                ["Swagger Petstore in Subfolder", "Swagger Petstore in Main"],
            )
            _check_page_title(browser, "subfolder/p2", ["Swagger Petstore in Specs"])
        finally:
            popen.terminate()


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
    builder: str, openapipage: str, petspage: str, rockspage: str, build_dir: str
) -> None:
    """Test referencing specifications from a variety of directories."""
    subprocess.run(
        [
            "sphinx-build",
            "-b",
            builder,
            "tests/test_subdirs",
            build_dir,
        ],
        check=True,
    )

    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")

    with (
        webdriver.Remote("http://localhost:4444", options=options) as browser,
        subprocess.Popen(
            [
                "python",
                "-m",
                "http.server",
                "--directory",
                build_dir,
            ]
        ) as popen,
    ):
        time.sleep(5)
        try:
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
        finally:
            popen.terminate()


@pytest.mark.integration
def test_dirhtml(build_dir: str) -> None:
    """Test a dirhtml scenario."""
    subprocess.run(
        ["sphinx-build", "-M", "dirhtml", "tests/test_data", build_dir],
        check=True,
    )

    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")

    with (
        webdriver.Remote("http://localhost:4444", options=options) as browser,
        subprocess.Popen(
            [
                "python",
                "-m",
                "http.server",
                "--directory",
                f"{build_dir}/dirhtml",
            ]
        ) as popen,
    ):
        time.sleep(5)
        try:
            _check_page_title_dirhtml(browser, "openapi", ["Swagger Petstore in Main"])
            _check_page_title_dirhtml(
                browser,
                "subfolder/p1",
                ["Swagger Petstore in Subfolder", "Swagger Petstore in Main"],
            )
            _check_page_title_dirhtml(
                browser, "subfolder/p2", ["Swagger Petstore in Specs"]
            )
        finally:
            popen.terminate()


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
