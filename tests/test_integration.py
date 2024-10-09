"""Integration tests."""

from __future__ import annotations

import shutil
import subprocess
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


@pytest.mark.integration
def test() -> None:
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
        browser.get("http://localhost:8000/openapi.html")
        title = browser.find_element(By.CLASS_NAME, "title")
        assert title.text.split("\n")[0] == "Swagger Petstore"
        popen.terminate()
