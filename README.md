# ROSLauncher

Simple desktop launcher for toggling a game mod and launching the game executable.

## Features

- Enable mod (moves/renames configured file path from disabled → enabled)
- Disable mod (moves/renames configured file path from enabled → disabled)
- Launch game executable
- Settings dialog to configure paths

## Requirements

- Python 3.9+ (includes `tkinter` on most Windows installs)

## Run

```bash
python launcher.py
```

## First-time setup

1. Open **Settings**.
2. Set **Game EXE** to your game executable path.
3. Set **Mod Disabled File** to the mod file location when mod is off.
4. Set **Mod Enabled File** to the mod file location when mod is on.
5. Click **Save**.

Settings are stored in `launcher_settings.json` in the same directory.
