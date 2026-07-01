from __future__ import annotations

try:
    import addonHandler
    import globalPluginHandler
except Exception:  # pragma: no cover - NVDA is not installed in test environment.
    addonHandler = None
    globalPluginHandler = None

if addonHandler is not None:
    addonHandler.initTranslation()

from .config import DEFAULT_CONFIG, get_config_path, load_config
from .settings import SpeechStylesSettingsPanel
from .style_engine import StyleEngine


if globalPluginHandler is not None:

    class GlobalPlugin(globalPluginHandler.GlobalPlugin):
        def __init__(self):
            super().__init__()
            self._config_path = get_config_path()
            self._config_mtime = None
            self._config = load_config(self._config_path)
            self._style_engine = StyleEngine(self._config.get("active_style", DEFAULT_CONFIG["active_style"]))
            self._register_settings_panel()

        def event_foreground(self, obj, nextHandler):
            nextHandler()
            self._speak_styled_object(obj, "foreground_window")

        def event_gainFocus(self, obj, nextHandler):
            nextHandler()
            element_name = self._element_name_for_object(obj)
            if element_name:
                self._speak_styled_object(obj, element_name)

        def terminate(self):
            self._unregister_settings_panel()
            super().terminate()

        def _register_settings_panel(self):
            try:
                import gui.settingsDialogs

                categories = gui.settingsDialogs.NVDASettingsDialog.categoryClasses
                if SpeechStylesSettingsPanel not in categories:
                    categories.append(SpeechStylesSettingsPanel)
            except Exception:
                pass

        def _unregister_settings_panel(self):
            try:
                import gui.settingsDialogs

                categories = gui.settingsDialogs.NVDASettingsDialog.categoryClasses
                if SpeechStylesSettingsPanel in categories:
                    categories.remove(SpeechStylesSettingsPanel)
            except Exception:
                pass

        def _reload_config_if_needed(self):
            try:
                mtime = self._config_path.stat().st_mtime
            except OSError:
                mtime = None
            if mtime == self._config_mtime:
                return
            self._config_mtime = mtime
            self._config = load_config(self._config_path)
            self._style_engine = StyleEngine(self._config.get("active_style", DEFAULT_CONFIG["active_style"]))

        def _element_name_for_object(self, obj):
            try:
                import controlTypes

                role_names = {}
                for role_name, element_name in (
                    ("BUTTON", "push_button"),
                    ("DROPDOWNBUTTON", "push_button"),
                    ("SPLITBUTTON", "push_button"),
                    ("TOGGLEBUTTON", "push_button"),
                    ("EDITABLETEXT", "edit"),
                    ("RICHEDIT", "edit"),
                    ("PASSWORDEDIT", "edit"),
                ):
                    role = getattr(controlTypes.Role, role_name, None)
                    if role is not None:
                        role_names[role] = element_name
                return role_names.get(obj.role)
            except Exception:
                return None

        def _speak_styled_object(self, obj, element_name):
            original = self._object_name(obj)
            if not original:
                return
            self._reload_config_if_needed()
            styled = self.transform(original, element_name)
            if styled == original:
                return
            try:
                import speech

                speech.cancelSpeech()
            except Exception:
                pass
            self._announce(styled)

        def _object_name(self, obj):
            try:
                return (obj.name or "").strip()
            except Exception:
                return ""

        def _announce(self, text):
            try:
                import ui

                ui.message(text)
            except Exception:
                pass

        def transform(self, original: str, element_name: str) -> str:
            return self._style_engine.transform(original, element_name, self._config)
else:

    class GlobalPlugin:  # pragma: no cover - fallback for import without NVDA.
        pass
