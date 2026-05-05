"""Derive plain-text lines from an OpenAPI document for search indexing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from sphinx.errors import ExtensionError

_HTTP_METHODS = frozenset(
    {"get", "post", "put", "patch", "delete", "head", "options", "trace"},
)
_DESCRIPTION_MAX_LEN = 500


def _append_description_line(
    lines: list[str],
    desc: Any,
    *,
    compare_to: str,
) -> None:
    if isinstance(desc, str) and desc.strip() and desc.strip() != compare_to.strip():
        snippet = desc.strip()
        if len(snippet) > _DESCRIPTION_MAX_LEN:
            snippet = snippet[: _DESCRIPTION_MAX_LEN - 3] + "..."
        lines.append(snippet)


def _schema_map_from_spec(spec: dict[str, Any]) -> dict[str, Any] | None:
    components = spec.get("components")
    if isinstance(components, dict):
        schemas = components.get("schemas")
        if isinstance(schemas, dict):
            return schemas
    definitions = spec.get("definitions")
    if isinstance(definitions, dict):
        return definitions
    return None


def _extend_schema_lines(lines: list[str], spec: dict[str, Any]) -> None:
    schemas = _schema_map_from_spec(spec)
    if not schemas:
        return
    for name in sorted(schemas):
        body = schemas[name]
        if not isinstance(body, dict):
            continue
        title = body.get("title")
        title_str = title.strip() if isinstance(title, str) and title.strip() else ""
        subtitle = title_str if title_str and title_str != str(name) else ""
        lines.append(f"Schema {name}" + (f" — {subtitle}" if subtitle else ""))
        _append_description_line(
            lines,
            body.get("description"),
            compare_to=title_str or str(name),
        )


def load_openapi_mapping(path: Path) -> dict[str, Any]:
    """Load a JSON or YAML OpenAPI file into a mapping."""
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
    """Build human-readable lines for search: API title, operations, and schemas."""
    lines: list[str] = []
    info = spec.get("info")
    if isinstance(info, dict):
        title = info.get("title")
        if title:
            version = info.get("version")
            lines.append(f"{title} {version}" if version else str(title))
    paths = spec.get("paths")
    if isinstance(paths, dict):
        for path in sorted(paths):
            path_item = paths[path]
            if not isinstance(path_item, dict):
                continue
            for method in sorted(path_item, key=str.lower):
                if str(method).lower() not in _HTTP_METHODS:
                    continue
                op = path_item[method]
                if not isinstance(op, dict):
                    continue
                summary = op.get("summary")
                op_id = op.get("operationId")
                label = summary if isinstance(summary, str) and summary.strip() else ""
                if not label and isinstance(op_id, str) and op_id.strip():
                    label = op_id.strip()
                upper = str(method).upper()
                line = f"{upper} {path}" + (f" — {label}" if label else "")
                lines.append(line)
                summary_cmp = summary.strip() if isinstance(summary, str) else ""
                _append_description_line(
                    lines,
                    op.get("description"),
                    compare_to=summary_cmp,
                )
    _extend_schema_lines(lines, spec)
    return lines
