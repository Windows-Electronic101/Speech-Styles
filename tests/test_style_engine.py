import json
import tempfile
from pathlib import Path

from addon.globalPlugins.speechStyles.style_engine import StyleEngine, build_phrase
from addon.globalPlugins.speechStyles.config import load_config, save_config, DEFAULT_CONFIG


def test_windows_xp_example_uses_foreground_window_prefix_and_comma_pause():
    engine = StyleEngine("windows_xp")
    phrase = engine.transform("Untitled - Notepad", "foreground_window")
    assert phrase == "Foreground Window, Untitled - Notepad"


def test_push_button_uses_comma_pause_before_control():
    engine = StyleEngine("windows_xp")
    phrase = engine.transform("OK", "push_button")
    assert phrase == "Push button, OK"


def test_config_round_trip_preserves_enabled_flags():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "speech_styles.json"
        cfg = DEFAULT_CONFIG.copy()
        cfg["active_style"] = "windows_10_narrator"
        cfg["elements"]["foreground_window"]["enabled"] = False
        save_config(cfg, path)
        loaded = load_config(path)
        assert loaded["active_style"] == "windows_10_narrator"
        assert loaded["elements"]["foreground_window"]["enabled"] is False


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
