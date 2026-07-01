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
from .style_engine import StyleEngine, transform_speech_sequence_for_element


def should_style_foreground_object(obj):
    name = object_name_without_shortcut(obj)
    if not name:
        return False
    if is_transient_shell_switcher(obj, name):
        return False
    return True


def is_transient_shell_switcher(obj, name):
    normalized_name = name.casefold()
    if normalized_name in {"task switching", "task switcher"}:
        return True
    try:
        class_name = (obj.windowClassName or "").casefold()
    except Exception:
        class_name = ""
    return class_name in {
        "multitaskingviewframe",
        "xaml_multitaskingviewframe",
        "windows.ui.core.corewindow",
    } and "task" in normalized_name


def object_name_without_shortcut(obj):
    try:
        return (obj.name or "").strip()
    except Exception:
        return ""


if globalPluginHandler is not None:

    class GlobalPlugin(globalPluginHandler.GlobalPlugin):
        def __init__(self):
            super().__init__()
            self._config_path = get_config_path()
            self._config_mtime = None
            self._config = load_config(self._config_path)
            self._style_engine = StyleEngine(self._config.get("active_style", DEFAULT_CONFIG["active_style"]))
            self._focus_speech_context = None
            self._register_settings_panel()
            self._register_speech_filter()

        def event_foreground(self, obj, nextHandler):
            nextHandler()
            if not self._should_style_foreground_object(obj):
                return
            self._speak_styled_object(obj, "foreground_window")

        def event_gainFocus(self, obj, nextHandler):
            element_name = self._element_name_for_object(obj)
            self._focus_speech_context = self._build_focus_speech_context(obj, element_name)
            try:
                nextHandler()
            finally:
                self._focus_speech_context = None

        def terminate(self):
            self._unregister_speech_filter()
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

        def _register_speech_filter(self):
            try:
                from speech.extensions import filter_speechSequence

                filter_speechSequence.register(self._filter_speech_sequence)
            except Exception:
                pass

        def _unregister_speech_filter(self):
            try:
                from speech.extensions import filter_speechSequence

                filter_speechSequence.unregister(self._filter_speech_sequence)
            except Exception:
                pass

        def _filter_speech_sequence(self, speechSequence):
            context = self._focus_speech_context
            if not context:
                return speechSequence
            self._reload_config_if_needed()
            return transform_speech_sequence_for_element(
                speechSequence,
                original=context["name"],
                element_name=context["element_name"],
                style_name=self._config.get("active_style", DEFAULT_CONFIG["active_style"]),
                config=self._config,
                role_labels=context["role_labels"],
                keyboard_shortcut=context["keyboard_shortcut"],
            )

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

        def _build_focus_speech_context(self, obj, element_name):
            if element_name != "push_button":
                return None
            name = self._object_name_without_shortcut(obj)
            if not name:
                return None
            return {
                "element_name": element_name,
                "name": name,
                "keyboard_shortcut": self._object_keyboard_shortcut(obj),
                "role_labels": self._role_labels_for_object(obj),
            }

        def _role_labels_for_object(self, obj):
            labels = {"button", "push button"}
            try:
                role_text = getattr(obj, "roleText", "")
                if role_text:
                    labels.add(role_text)
            except Exception:
                pass
            try:
                role_display = getattr(obj.role, "displayString", "")
                if role_display:
                    labels.add(role_display)
            except Exception:
                pass
            return tuple(labels)

        def _should_style_foreground_object(self, obj):
            return should_style_foreground_object(obj)

        def _speak_styled_object(self, obj, element_name):
            original = self._object_name(obj)
            if not original:
                return
            self._reload_config_if_needed()
            styled = self.transform(original, element_name)
            if styled == original:
                return
            self._announce(styled)

        def _object_name(self, obj):
            try:
                parts = [self._object_name_without_shortcut(obj)]
                keyboard_shortcut = self._object_keyboard_shortcut(obj)
                if keyboard_shortcut and self._should_report_keyboard_shortcuts():
                    parts.append(keyboard_shortcut)
                return " ".join(part for part in parts if part)
            except Exception:
                return ""

        def _object_name_without_shortcut(self, obj):
            return object_name_without_shortcut(obj)

        def _object_keyboard_shortcut(self, obj):
            if not self._should_report_keyboard_shortcuts():
                return ""
            try:
                return (obj.keyboardShortcut or "").strip()
            except Exception:
                return ""

        def _should_report_keyboard_shortcuts(self):
            try:
                import config

                return bool(config.conf["presentation"]["reportKeyboardShortcuts"])
            except Exception:
                return True

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
