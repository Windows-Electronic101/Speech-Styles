import json
import tempfile
from pathlib import Path

from addon.globalPlugins.speechStyles.style_engine import (
    StyleEngine,
    build_phrase,
    transform_speech_sequence_for_element,
)
from addon.globalPlugins.speechStyles.config import load_config, save_config, DEFAULT_CONFIG


def test_windows_xp_foreground_window_uses_role_before_title():
    engine = StyleEngine("windows_xp")
    phrase = engine.transform("Untitled - Notepad", "foreground_window")
    assert phrase == "Foreground Window, Untitled - Notepad"


def test_windows_xp_push_button_uses_label_before_role():
    engine = StyleEngine("windows_xp")
    phrase = engine.transform("OK", "push_button")
    assert phrase == "OK Button"


def test_config_round_trip_preserves_enabled_flags():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "speech_styles.json"
        cfg = DEFAULT_CONFIG.copy()
        cfg["active_style"] = "windows_10_narrator"
        cfg["elements"] = {"foreground_window": {"enabled": False}}
        save_config(cfg, path)
        loaded = load_config(path)
        assert loaded["active_style"] == "windows_10_narrator"
        assert loaded["elements"]["foreground_window"]["enabled"] is False


def test_default_config_does_not_override_selected_preset():
    engine = StyleEngine("windows_10_narrator")
    phrase = engine.transform("Untitled - Notepad", "foreground_window", DEFAULT_CONFIG)
    assert phrase == "Untitled - Notepad. Foreground Window"


def test_build_phrase_supports_after_position_and_period_pause():
    phrase = build_phrase(
        original="Edit box",
        element_name="edit",
        style_name="windows_10_narrator",
        config={
            "elements": {
                "edit": {
                    "enabled": True,
                    "label": "Edit box",
                    "pause": "period",
                    "position": "after",
                }
            }
        },
    )
    assert phrase == "Edit box. Edit box"


def test_focus_speech_sequence_rewrites_button_without_dropping_shortcut():
    sequence = ["Do you want to continue?", "Yes", "Alt+Y", "button"]
    rewritten = transform_speech_sequence_for_element(
        sequence,
        original="Yes",
        element_name="push_button",
        style_name="windows_xp",
        config=DEFAULT_CONFIG,
        role_labels=("button", "push button"),
        keyboard_shortcut="Alt+Y",
    )
    assert rewritten == ["Do you want to continue?", "Yes Button", "Alt+Y"]


def test_focus_speech_sequence_does_not_duplicate_shortcut_after_role():
    sequence = ["Do you want to continue?", "Yes", "button", "Alt+Y"]
    rewritten = transform_speech_sequence_for_element(
        sequence,
        original="Yes",
        element_name="push_button",
        style_name="windows_xp",
        config=DEFAULT_CONFIG,
        role_labels=("button", "push button"),
        keyboard_shortcut="Alt+Y",
    )
    assert rewritten == ["Do you want to continue?", "Yes Button", "Alt+Y"]


def test_focus_speech_sequence_preserves_expanded_shortcut_once():
    sequence = ["Do you want to continue?", "Yes", "Alt", "+", "Y", "button"]
    rewritten = transform_speech_sequence_for_element(
        sequence,
        original="Yes",
        element_name="push_button",
        style_name="windows_xp",
        config=DEFAULT_CONFIG,
        role_labels=("button", "push button"),
        keyboard_shortcut="Alt+Y",
    )
    assert rewritten == ["Do you want to continue?", "Yes Button", "Alt", "+", "Y"]


def test_focus_speech_sequence_uses_before_style_without_duplicate_role():
    sequence = ["Do you want to continue?", "Yes", "Alt+Y", "button"]
    rewritten = transform_speech_sequence_for_element(
        sequence,
        original="Yes",
        element_name="push_button",
        style_name="windows_7_narrator",
        config=DEFAULT_CONFIG,
        role_labels=("button", "push button"),
        keyboard_shortcut="Alt+Y",
    )
    assert rewritten == ["Do you want to continue?", "Push button, Yes", "Alt+Y"]
