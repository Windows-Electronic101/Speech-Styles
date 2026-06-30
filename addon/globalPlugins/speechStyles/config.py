from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_CONFIG: Dict[str, Any] = {
    "active_style": "windows_10_narrator",
    "elements": {
        "foreground_window": {
            "enabled": True,
            "label": "Foreground Window",
            "pause": "comma",
            "position": "before",
        },
        "push_button": {
            "enabled": True,
            "label": "Push button",
            "pause": "comma",
            "position": "before",
        },
        "edit": {
            "enabled": True,
            "label": "Edit box",
            "pause": "none",
            "position": "none",
        },
    },
}


def load_config(path: Optional[Path] = None) -> Dict[str, Any]:
    if path is None:
        path = Path(__file__).resolve().parent / "speech_styles.json"
    if not path.exists():
        return deepcopy(DEFAULT_CONFIG)

    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    merged = deepcopy(DEFAULT_CONFIG)
    if isinstance(raw, dict):
        merged.update(raw)
        for element_id, element_config in raw.get("elements", {}).items():
            if not isinstance(element_config, dict):
                continue
            merged.setdefault("elements", {})
            merged["elements"].setdefault(element_id, {})
            merged["elements"][element_id].update(element_config)
    return merged


def save_config(config: Dict[str, Any], path: Optional[Path] = None) -> Path:
    if path is None:
        path = Path(__file__).resolve().parent / "speech_styles.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2, ensure_ascii=False)
    return path
