from __future__ import annotations

try:
    import wx
except Exception:  # pragma: no cover - wxPython is not available in the test environment.
    wx = None

try:
    from gui.settingsDialogs import SettingsPanel as NVDASettingsPanel
except Exception:  # pragma: no cover - NVDA is not installed in test environment.
    if wx is not None:
        class NVDASettingsPanel(wx.Panel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
    else:
        class NVDASettingsPanel:
            def __init__(self, *args, **kwargs):
                pass

from .config import load_config, save_config


class SpeechStylesSettingsPanel(NVDASettingsPanel):
    title = "Speech Styles"

    def __init__(self, parent, panel_id=None):
        try:
            super().__init__(parent, panel_id)
        except TypeError:  # pragma: no cover - compatibility fallback for non-NVDA wx.
            super().__init__(parent)
        self.config_path = None
        self.config = load_config()
        self._controls = {}
        self._build_ui()

    def _build_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        style_label = wx.StaticText(self, label="Style:")
        style_choice = wx.Choice(self, choices=["windows_10_narrator", "windows_xp", "windows_7_narrator", "jaws"])
        style_choice.SetStringSelection(self.config.get("active_style", "windows_10_narrator"))
        self._controls["active_style"] = style_choice
        sizer.Add(style_label, 0, wx.ALL, 5)
        sizer.Add(style_choice, 0, wx.ALL, 5)

        for element_id, element_config in self.config.get("elements", {}).items():
            row = wx.BoxSizer(wx.HORIZONTAL)
            checkbox = wx.CheckBox(self, label=element_config.get("label", element_id.replace("_", " ")))
            checkbox.SetValue(bool(element_config.get("enabled", True)))
            self._controls[(element_id, "enabled")] = checkbox

            pause_choice = wx.Choice(self, choices=["none", "comma", "period"])
            pause_choice.SetStringSelection(element_config.get("pause", "none"))
            self._controls[(element_id, "pause")] = pause_choice

            position_choice = wx.Choice(self, choices=["none", "before", "after"])
            position_choice.SetStringSelection(element_config.get("position", "none"))
            self._controls[(element_id, "position")] = position_choice

            row.Add(checkbox, 0, wx.ALL, 5)
            row.Add(wx.StaticText(self, label="Pause:"), 0, wx.ALL, 5)
            row.Add(pause_choice, 0, wx.ALL, 5)
            row.Add(wx.StaticText(self, label="Position:"), 0, wx.ALL, 5)
            row.Add(position_choice, 0, wx.ALL, 5)
            sizer.Add(row, 0, wx.ALL, 5)

        self.SetSizer(sizer)
        self.Layout()

    def onSave(self):
        self._save()

    def _save(self):
        self.config["active_style"] = self._controls["active_style"].GetStringSelection()
        for element_id, element_config in self.config.get("elements", {}).items():
            checkbox = self._controls[(element_id, "enabled")]
            pause_choice = self._controls[(element_id, "pause")]
            position_choice = self._controls[(element_id, "position")]
            element_config["enabled"] = bool(checkbox.GetValue())
            element_config["pause"] = pause_choice.GetStringSelection()
            element_config["position"] = position_choice.GetStringSelection()
        save_config(self.config, self.config_path)

    def save(self):
        self._save()
