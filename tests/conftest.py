"""Main conftest."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def testdata(tmp_path: Path) -> Path:
    """Generate test data."""
    root = Path("tests/test_data")
    spec = Path("tests/openapi.yml")

    test_folder = tmp_path / "testdata"
    shutil.copytree(root, test_folder)

    locations = [
        (test_folder / "openapi_main.yml", "Swagger Petstore in Main"),
        (test_folder / "specs/openapi_specs.yml", "Swagger Petstore in Specs"),
        (test_folder / "specs/petstore/openapi_specs.yml", "Swagger Petstore in Specs"),
        (
            test_folder / "specs/rockstore/openapi_specs.yml",
            "Swagger Rockstore in Specs",
        ),
        (
            test_folder / "subfolder/openapi_subfolder.yml",
            "Swagger Petstore in Subfolder",
        ),
        (test_folder / "stores/openapi_samedir.yml", "Swagger Petstore in Samedir"),
        (
            test_folder / "stores/rockstore/specs/openapi_childdir.yml",
            "Swagger Petstore in Childdir",
        ),
    ]
    for path, title in locations:
        shutil.copyfile(spec, path)
        _adjust_title(path, title)

    return test_folder


def _adjust_title(path: Path, title: str) -> None:
    with path.open(encoding="utf-8") as file:
        data = yaml.load(file, yaml.Loader)
    data["info"]["title"] = title
    with path.open("w", encoding="utf-8") as file:
        yaml.dump(data, file, Dumper=yaml.Dumper)
