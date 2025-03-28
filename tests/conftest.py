"""Main conftest."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def testdata(tmp_path: Path) -> Path:
    """Generate test data."""
    root = Path("tests/testdata")
    spec = Path("tests/openapi.yml")

    test_folder = tmp_path / "testdata"
    test_folder.mkdir()
    shutil.copytree(root, test_folder)

    locations = [
        (test_folder / "openapi_main.yaml", "Swagger Petstore in Main"),
        (test_folder / "specs/openapi_specs.yaml", "Swagger Petstore in Specs"),
        (
            test_folder / "subfolder/openapi_subfolder.yaml",
            "Swagger Petstore in Subfolder",
        ),
        (test_folder / "stores/openapi_samedir.yaml", "Swagger Petstore in Samedir"),
        (
            test_folder / "stores/rockstore/specs/openapi_childdir.yaml",
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
