# Speech Styles

This repository now contains a functional NVDA add-on scaffold for Speech Styles, targeting NVDA 2025.4.x and later-compatible add-on packaging conventions.

## Features

- Switch between built-in speech styles such as Windows 10 Narrator, Windows XP, Windows 7 Narrator, and JAWS.
- Customize each UI element announcement with a dedicated settings panel in NVDA.
- Use checkboxes to enable or disable per-element rules; when disabled, NVDA falls back to its default announcement.
- Choose a pause style for each element: none, comma, or period.
- Choose where the UI type is announced: before, after, or not at all.

## Structure

- addon/globalPlugins/speechStyles/config.py: persistent JSON configuration and defaults
- addon/globalPlugins/speechStyles/style_engine.py: style transformation logic
- addon/globalPlugins/speechStyles/settings.py: settings panel UI for NVDA
- addon/globalPlugins/speechStyles/addon.py: addon entry point and registration
- manifest.ini: add-on metadata for recent NVDA versions

## Verification

Run the regression tests with:

python -m pytest -q
