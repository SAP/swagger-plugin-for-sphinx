"""Derive plain-text lines from an OpenAPI document for search indexing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from sphinx.errors import ExtensionError

_HTTP_METHODS = frozenset(
    ("GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE")
)
_DESCRIPTION_MAX_LEN = 500


def _append_description_line(lines: list[str], desc: Any, *, compare_to: str) -> None:
    """Append a description line to the text for the search index."""
    # Skip if identical to the summary/title to avoid duplication.
    if isinstance(desc, str) and desc.strip() and desc.strip() != compare_to.strip():
        snippet = desc.strip()
        if len(snippet) > _DESCRIPTION_MAX_LEN:
            snippet = snippet[: _DESCRIPTION_MAX_LEN - 3] + "..."
        lines.append(snippet)


def _get_schemas(spec: dict[str, Any]) -> dict[str, Any] | None:
    """Return text from the schema section of the spec for use in the search index."""
    # Components are part of the OpenAPI 3.x specification.
    components = spec.get("components")
    if isinstance(components, dict):
        schemas = components.get("schemas")
        if isinstance(schemas, dict):
            return schemas
    # For 2.0, use top-level definitions.
    definitions = spec.get("definitions")
    if isinstance(definitions, dict):
        return definitions
    return None


def _extend_schema_lines(spec: dict[str, Any], lines: list[str]) -> None:
    """Add key fields from the schema objects to the search index."""
    schemas = _get_schemas(spec)
    if not schemas:
        return
    for name, schema in schemas.items():
        if not isinstance(schema, dict):
            continue
        raw_title = schema.get("title")
        title_str = raw_title.strip() if isinstance(raw_title, str) else ""
        suffix = f" — {title_str}" if title_str and title_str != str(name) else ""
        lines.append(f"Schema {name}{suffix}")
        _append_description_line(
            lines, schema.get("description"), compare_to=title_str or str(name)
        )


def load_openapi_file(path: Path) -> dict[str, Any]:
    """Load a JSON or YAML OpenAPI file."""
    raw = path.read_text(encoding="utf-8")
    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError:
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            raise ExtensionError(f"Could not parse OpenAPI file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ExtensionError(f"OpenAPI document must be a mapping: {path}")
    return data


def _handle_openapi_info(spec: dict[str, Any], lines: list[str]) -> None:
    info = spec.get("info")
    if not isinstance(info, dict):
        return
    title = info.get("title")
    if not title:
        return
    version = info.get("version")
    lines.append(f"{title} {version}" if version else str(title))


def _handle_paths(spec: dict[str, Any], lines: list[str]) -> None:
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        return
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, op in path_item.items():
            if method.lower() not in _HTTP_METHODS or not isinstance(op, dict):
                continue
            raw_summary = op.get("summary")
            summary = raw_summary.strip() if isinstance(raw_summary, str) else ""
            raw_op_id = op.get("operationId")
            op_id = raw_op_id.strip() if isinstance(raw_op_id, str) else ""
            label = summary or op_id
            suffix = f" — {label}" if label else ""
            lines.append(f"{method.upper()} {path}{suffix}")
            _append_description_line(lines, op.get("description"), compare_to=summary)


def openapi_lines_for_search(spec: dict[str, Any]) -> list[str]:
    """Build human-readable lines from the spec for the search index."""
    lines: list[str] = []
    _handle_openapi_info(spec, lines)
    _handle_paths(spec, lines)
    _extend_schema_lines(spec, lines)
    return lines
