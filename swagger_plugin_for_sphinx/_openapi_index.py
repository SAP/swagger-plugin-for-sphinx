"""Derive plain-text lines from an OpenAPI document for search indexing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from sphinx.errors import ExtensionError
from sphinx.util import logging

_HTTP_METHODS = frozenset(
    {"get", "post", "put", "patch", "delete", "head", "options", "trace"},
)
_DESCRIPTION_MAX_LEN = 500
logger = logging.getLogger(__name__)


def _check_for_string(val: Any) -> str:
    """Defensive check for string values in OpenAPI spec fields."""
    if isinstance(val, str):
        return val.strip()
    if val is not None:
        logger.warning("Expected a string value, got %s: %r", type(val).__name__, val)
    return ""


def _append_description_line(
    lines: list[str],
    desc: Any,
    *,
    compare_to: str,
) -> None:
    """Append a description line to the text for the search index."""
    # If the description is identical to the summary/title, skip it.
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


def _extend_schema_lines(lines: list[str], spec: dict[str, Any]) -> None:
    """Add key fields from the schema objects to the search index."""
    schemas = _get_schemas(spec)
    if not schemas:
        return
    for name in schemas:  # "Pet"
        schema = schemas[name]  # {"type": "object", "title": "A Pet", ...}
        if not isinstance(schema, dict):
            continue
        title_str = _check_for_string(schema.get("title"))
        suffix = f" — {title_str}" if title_str and title_str != str(name) else ""
        lines.append(f"Schema {name}{suffix}")  # "Schema Pet — A Pet"
        _append_description_line(
            lines,
            schema.get("description"),
            compare_to=title_str or str(name),
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


def openapi_lines_for_search(spec: dict[str, Any]) -> list[str]:
    """Build human-readable lines from the spec for the search index.

    Get the API title, operations, and schemas.
    """
    lines: list[str] = []
    # Get the API title and version.
    info = spec.get("info")
    if isinstance(info, dict):
        title = info.get("title")
        if title:
            version = info.get("version")
            lines.append(f"{title} {version}" if version else str(title))
    # Get the endpoints and methods.
    paths = spec.get("paths")
    if isinstance(paths, dict):
        for path in paths:  # "/pets"
            if not isinstance(paths[path], dict):
                continue
            for method in paths[path]:  # "get"
                if str(method).lower() not in _HTTP_METHODS:
                    continue
                op = paths[path][method]  # {"summary": "List all pets", ...}
                if not isinstance(op, dict):
                    continue
                summary = _check_for_string(op.get("summary"))  # "List all pets"
                label = summary or _check_for_string(op.get("operationId"))
                suffix = f" — {label}" if label else ""
                lines.append(
                    f"{str(method).upper()} {path}{suffix}"
                )  # "GET /pets — List all pets"
                _append_description_line(
                    lines,
                    op.get("description"),
                    compare_to=summary,
                )
    _extend_schema_lines(lines, spec)
    return lines
