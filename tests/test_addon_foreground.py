from addon.globalPlugins.speechStyles.addon import should_style_foreground_object


class FakeObject:
    def __init__(self, name, window_class_name=""):
        self.name = name
        self.windowClassName = window_class_name
        self.keyboardShortcut = ""


def test_task_switching_foreground_is_not_styled():
    obj = FakeObject("Task Switching")

    assert should_style_foreground_object(obj) is False


def test_selected_app_foreground_is_styled():
    obj = FakeObject("Untitled - Notepad")

    assert should_style_foreground_object(obj) is True
