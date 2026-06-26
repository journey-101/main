from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_payload(data_dir: Path, filename: str, context: dict[str, str]) -> dict[str, Any]:
    path = data_dir / filename
    with path.open(encoding="utf-8") as payload_file:
        payload = json.load(payload_file)

    rendered = _render_value(payload, context)
    if not isinstance(rendered, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return rendered


def _render_value(value: Any, context: dict[str, str]) -> Any:
    if isinstance(value, str):
        rendered = value
        for key, replacement in context.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", replacement)
        return rendered
    if isinstance(value, list):
        return [_render_value(item, context) for item in value]
    if isinstance(value, dict):
        return {key: _render_value(item, context) for key, item in value.items()}
    return value
