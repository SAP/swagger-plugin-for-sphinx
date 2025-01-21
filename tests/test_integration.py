"""Integration tests."""

from __future__ import annotations

import shutil
import subprocess
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


@pytest.mark.integration
def test_basic() -> None:
    """Test a basic scenario."""
    shutil.rmtree("tests/test_data/_build", ignore_errors=True)
    subprocess.run(
        ["sphinx-build", "tests/test_data", "tests/test_data/_build"], check=True
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
                "tests/test_data/_build/",
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
def test_dirhtml() -> None:
    """Test a dirhtml scenario."""
    shutil.rmtree("tests/test_data/_build", ignore_errors=True)
    subprocess.run(
        ["sphinx-build", "-M", "dirhtml", "tests/test_data", "tests/test_data/_build"],
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
                "tests/test_data/_build/dirhtml",
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
