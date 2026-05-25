"""Tests for OpenAPI → search lines."""

from __future__ import annotations

from pathlib import Path

import pytest
from sphinx.errors import ExtensionError

from swagger_plugin_for_sphinx._openapi_index import (
    load_openapi_file,
    openapi_lines_for_search,
)


def test_openapi_lines_for_search() -> None:
    spec_path = Path(__file__).with_name("openapi.yml")
    spec = load_openapi_file(spec_path)
    lines = openapi_lines_for_search(spec)
    assert "Swagger Petstore 1.0.0" in lines
    assert "GET /pets — List all pets" in lines
    assert "POST /pets — Create a pet" in lines
    assert "GET /pets/{petId} — Info for a specific pet" in lines
    assert "Schema Error" in lines
    assert "Schema Pet" in lines
    assert "Schema Pets" in lines


def test_openapi_lines_title_without_version() -> None:
    lines = openapi_lines_for_search({"info": {"title": "OnlyTitle"}})
    assert lines == ["OnlyTitle"]


def test_openapi_lines_paths_not_mapping() -> None:
    lines = openapi_lines_for_search({"info": {"title": "T"}, "paths": []})
    assert lines == ["T"]


def test_openapi_lines_skips_bad_path_or_operation() -> None:
    lines = openapi_lines_for_search(
        {
            "paths": {
                "/bad-item": "not-a-mapping",
                "/b": {"get": "not-an-operation"},
            },
        },
    )
    assert not lines


def test_openapi_lines_operation_id_without_summary() -> None:
    lines = openapi_lines_for_search(
        {"paths": {"/x": {"get": {"operationId": "fetchX"}}}},
    )
    assert lines == ["GET /x — fetchX"]


def test_openapi_lines_non_method_path_keys_skipped() -> None:
    lines = openapi_lines_for_search(
        {
            "paths": {
                "/x": {
                    "parameters": [],
                    "get": {"summary": "G"},
                },
            },
        },
    )
    assert lines == ["GET /x — G"]


def test_openapi_lines_info_dict_but_no_title() -> None:
    assert not openapi_lines_for_search({"info": {}})


def test_openapi_lines_schemas_when_paths_not_mapping() -> None:
    lines = openapi_lines_for_search(
        {
            "info": {"title": "T"},
            "paths": [],
            "components": {"schemas": {"Pet": {"type": "object"}}},
        },
    )
    assert lines[0] == "T"
    assert "Schema Pet" in lines


def test_openapi_lines_swagger2_definitions() -> None:
    lines = openapi_lines_for_search(
        {
            "swagger": "2.0",
            "definitions": {"Widget": {"type": "object", "title": "W"}},
        },
    )
    assert "Schema Widget — W" in lines


def test_openapi_lines_schema_description() -> None:
    lines = openapi_lines_for_search(
        {
            "components": {
                "schemas": {
                    "M": {
                        "type": "object",
                        "description": "A model for things.",
                    },
                },
            },
        },
    )
    assert "Schema M" in lines
    assert "A model for things." in lines


def test_openapi_lines_skips_non_mapping_schema_body() -> None:
    lines = openapi_lines_for_search(
        {"components": {"schemas": {"X": "broken"}}},
    )
    assert not lines


def test_openapi_lines_components_not_dict() -> None:
    lines = openapi_lines_for_search({"components": "no", "paths": {}})
    assert not lines


def test_openapi_lines_definitions_when_component_schemas_invalid() -> None:
    lines = openapi_lines_for_search(
        {
            "components": {"schemas": "not-a-map"},
            "definitions": {"D": {"type": "object"}},
        },
    )
    assert lines == ["Schema D"]


def test_openapi_lines_description_omitted_when_same_as_summary() -> None:
    lines = openapi_lines_for_search(
        {
            "paths": {
                "/x": {"get": {"summary": "Same", "description": "Same"}},
            },
        },
    )
    assert lines == ["GET /x — Same"]


def test_openapi_lines_description_truncated() -> None:
    long_desc = "a" * 600
    lines = openapi_lines_for_search(
        {
            "paths": {
                "/x": {
                    "get": {"summary": "S", "description": long_desc},
                },
            },
        },
    )
    assert "GET /x — S" in lines
    excerpt = [line for line in lines if line.startswith("a")]
    assert len(excerpt) == 1
    assert excerpt[0].endswith("...")
    assert len(excerpt[0]) == 500


def test_openapi_lines_extra_description_line() -> None:
    lines = openapi_lines_for_search(
        {
            "paths": {
                "/x": {
                    "get": {"summary": "S", "description": "Extra detail"},
                },
            },
        },
    )
    assert lines == ["GET /x — S", "Extra detail"]


def test_load_openapi_invalid_yaml(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("foo: [", encoding="utf-8")
    with pytest.raises(ExtensionError, match="Could not parse"):
        load_openapi_file(bad)


def test_load_openapi_not_mapping(tmp_path: Path) -> None:
    listed = tmp_path / "list.yaml"
    listed.write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(ExtensionError, match="must be a mapping"):
        load_openapi_file(listed)


def test_load_json(tmp_path: Path) -> None:
    j = tmp_path / "x.json"
    j.write_text('{"info": {"title": "T"}, "paths": {}}', encoding="utf-8")
    spec = load_openapi_file(j)
    assert openapi_lines_for_search(spec) == ["T"]
