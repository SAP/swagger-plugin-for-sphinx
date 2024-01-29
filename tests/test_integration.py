"""Integration tests."""

import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import subprocess
import shutil


@pytest.mark.integration
def test() -> None:
    shutil.rmtree("tests/test_data/_build", ignore_errors=True)
    subprocess.run(
        ["sphinx-build", "tests/test_data", "tests/test_data/_build"], check=True
    )

    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    selenium_host = os.environ["SELENIUM"]

    with (
        webdriver.Remote(f"{selenium_host}:4444", options=options) as browser,
        subprocess.Popen(
            [
                "python",
                "-m",
                "http.server",
                "--directory",
                "tests/test_data/_build/",
            ],
        ) as popen,
    ):
        browser.get("http://localhost:8000/openapi.html")
        title = browser.find_element(By.CLASS_NAME, "title")
        assert title.text.split("\n")[0] == "Swagger Petstore"
        popen.terminate()
