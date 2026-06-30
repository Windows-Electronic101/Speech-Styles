from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    import globalPluginHandler
    import globalVars
except Exception:  # pragma: no cover - NVDA is not installed in test environment.
    globalPluginHandler = None
    globalVars = None

from .config import DEFAULT_CONFIG, load_config
from .style_engine import StyleEngine


def get_config_path() -> Optional[Path]:
    if globalVars is not None:
        try:
            config_path = getattr(globalVars.appArgs, "configPath", None)
            if config_path:
                return Path(config_path) / "speech_styles.json"
        except Exception:
            pass
    return Path(__file__).resolve().parent / "speech_styles.json"


if globalPluginHandler is not None:
    class GlobalPlugin(globalPluginHandler.GlobalPlugin):
        def __init__(self):
            super().__init__()
            self._config_path = get_config_path()
            self._config = load_config(self._config_path)
            self._style_engine = StyleEngine(self._config.get("active_style", DEFAULT_CONFIG["active_style"]))

        def script_toggle(self, gesture):
            self._config["active_style"] = "windows_xp" if self._config.get("active_style") == "windows_10_narrator" else "windows_10_narrator"
            self._style_engine = StyleEngine(self._config["active_style"])
            self._announce("Switched style")

        def _announce(self, text):
            try:
                import speech

                speech.speakMessage(text)
            except Exception:
                pass

        def transform(self, original: str, element_name: str) -> str:
            return self._style_engine.transform(original, element_name, self._config)
else:
    class GlobalPlugin:  # pragma: no cover - fallback for import without NVDA.
        pass
