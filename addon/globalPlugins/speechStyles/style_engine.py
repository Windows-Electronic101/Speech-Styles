from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Optional

STYLE_PRESETS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "windows_10_narrator": {
        "foreground_window": {
            "enabled": True,
            "label": "Foreground Window",
            "pause": "period",
            "position": "after",
        },
        "push_button": {
            "enabled": True,
            "label": "Push button",
            "pause": "none",
            "position": "after",
        },
    },
    "windows_xp": {
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
    },
    "windows_7_narrator": {
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
    },
    "jaws": {
        "foreground_window": {
            "enabled": True,
            "label": "Window",
            "pause": "comma",
            "position": "before",
        },
        "push_button": {
            "enabled": True,
            "label": "Button",
            "pause": "comma",
            "position": "before",
        },
    },
}


class StyleEngine:
    def __init__(self, style_name: str = "windows_10_narrator"):
        self.style_name = style_name

    def transform(self, original: str, element_name: str, config: Optional[Dict[str, Any]] = None) -> str:
        if not original:
            return original

        style_config = deepcopy(STYLE_PRESETS.get(self.style_name, STYLE_PRESETS["windows_10_narrator"]))
        if config:
            element_style = config.get("elements", {}).get(element_name, {})
            if element_style:
                style_config[element_name] = {**style_config.get(element_name, {}), **element_style}

        element_config = style_config.get(element_name, {})
        if not element_config.get("enabled", True):
            return original
        return self._apply_style(original, element_name, element_config)

    def _apply_style(self, original: str, element_name: str, element_config: Dict[str, Any]) -> str:
        label = element_config.get("label", element_name.replace("_", " ").title())
        pause = element_config.get("pause", "none")
        position = element_config.get("position", "none")
        pause_text = "," if pause == "comma" else "." if pause == "period" else ""

        if position == "before":
            return f"{label}{pause_text} {original}".strip()
        if position == "after":
            return f"{original}{pause_text} {label}".strip()
        return original


def build_phrase(original: str, element_name: str, style_name: str, config: Dict[str, Any]) -> str:
    engine = StyleEngine(style_name)
    return engine.transform(original, element_name, config)
