from __future__ import annotations

try:
    import wx
except Exception:  # pragma: no cover - wxPython is not available in the test environment.
    wx = None

try:
    from gui.settingsDialogs import SettingsPanel as NVDASettingsPanel
except Exception:  # pragma: no cover - NVDA is not installed in the test environment.
    if wx is not None:

        class NVDASettingsPanel(wx.Panel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

    else:

        class NVDASettingsPanel:
            def __init__(self, *args, **kwargs):
                pass


from .config import get_config_path, load_config, save_config
from .style_engine import StyleEngine


class SpeechStylesSettingsPanel(NVDASettingsPanel):
    title = "Speech Styles"
    panelDescription = "Configure how Speech Styles changes supported UI element announcements."

    def __init__(self, parent):
        self.config_path = get_config_path()
        self.config = load_config(self.config_path)
        self._controls = {}
        self._style_names = StyleEngine.available_styles()
        super().__init__(parent)

    def makeSettings(self, sizer):
        if wx is None:
            return

        style_label = wx.StaticText(self, label="&Style:")
        style_choice = wx.Choice(
            self,
            choices=[StyleEngine.display_name(style_name) for style_name in self._style_names],
        )
        active_style = self.config.get("active_style", self._style_names[0])
        try:
            style_choice.SetSelection(self._style_names.index(active_style))
        except ValueError:
            style_choice.SetSelection(0)
        self._controls["active_style"] = style_choice

        sizer.Add(style_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        sizer.Add(style_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        for element_id, element_config in self.config.get("elements", {}).items():
            row = wx.BoxSizer(wx.HORIZONTAL)
            checkbox = wx.CheckBox(self, label=element_config.get("label", element_id.replace("_", " ")))
            checkbox.SetValue(bool(element_config.get("enabled", True)))
            self._controls[(element_id, "enabled")] = checkbox

            pause_label = wx.StaticText(self, label="Pause:")
            pause_choice = wx.Choice(self, choices=["none", "comma", "period"])
            pause_choice.SetStringSelection(element_config.get("pause", "none"))
            self._controls[(element_id, "pause")] = pause_choice

            position_label = wx.StaticText(self, label="Position:")
            position_choice = wx.Choice(self, choices=["none", "before", "after"])
            position_choice.SetStringSelection(element_config.get("position", "none"))
            self._controls[(element_id, "position")] = position_choice

            row.Add(checkbox, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
            row.Add(pause_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
            row.Add(pause_choice, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
            row.Add(position_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
            row.Add(position_choice, 0, wx.ALIGN_CENTER_VERTICAL)
            sizer.Add(row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

    def onSave(self):
        self._save()

    def save(self):
        self._save()

    def _save(self):
        selection = self._controls["active_style"].GetSelection()
        if selection < 0:
            selection = 0
        self.config["active_style"] = self._style_names[selection]

        for element_id, element_config in self.config.get("elements", {}).items():
            element_config["enabled"] = bool(self._controls[(element_id, "enabled")].GetValue())
            element_config["pause"] = self._controls[(element_id, "pause")].GetStringSelection()
            element_config["position"] = self._controls[(element_id, "position")].GetStringSelection()
        save_config(self.config, self.config_path)
