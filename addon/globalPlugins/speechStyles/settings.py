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
        style_choice.Bind(wx.EVT_CHOICE, self._on_style_changed)

        sizer.Add(style_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        sizer.Add(style_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        active_style = self._selected_style_name()
        for element_id, element_config in StyleEngine.elements_for_style(active_style, self.config).items():
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
        active_style = self._selected_style_name()
        self.config["active_style"] = active_style

        base_elements = StyleEngine.elements_for_style(active_style)
        custom_elements = {}
        for element_id, base_config in base_elements.items():
            element_config = {
                "enabled": bool(self._controls[(element_id, "enabled")].GetValue()),
                "label": self._controls[(element_id, "enabled")].GetLabel(),
                "pause": self._controls[(element_id, "pause")].GetStringSelection(),
                "position": self._controls[(element_id, "position")].GetStringSelection(),
            }
            custom_config = {
                key: value
                for key, value in element_config.items()
                if value != base_config.get(key)
            }
            if custom_config:
                custom_elements[element_id] = custom_config
        self.config["elements"] = custom_elements
        save_config(self.config, self.config_path)

    def _selected_style_name(self):
        selection = self._controls["active_style"].GetSelection()
        if selection < 0:
            selection = 0
        return self._style_names[selection]

    def _on_style_changed(self, event):
        element_configs = StyleEngine.elements_for_style(self._selected_style_name(), self.config)
        for element_id, element_config in element_configs.items():
            self._controls[(element_id, "enabled")].SetLabel(
                element_config.get("label", element_id.replace("_", " ")),
            )
            self._controls[(element_id, "enabled")].SetValue(bool(element_config.get("enabled", True)))
            self._controls[(element_id, "pause")].SetStringSelection(element_config.get("pause", "none"))
            self._controls[(element_id, "position")].SetStringSelection(element_config.get("position", "none"))
        event.Skip()
