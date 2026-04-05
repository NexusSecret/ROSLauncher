# ROSLauncher

Simple desktop launcher for toggling a game mod and launching the game executable.

## Features

- Toggle mod with one button (Enable/Disable)
- Launch `lotrbfme.exe` from the selected game folder
- Settings dialog to configure game folder

## Requirements

- Python 3.9+ (includes `tkinter` on most Windows installs)

## Run

```bash
python launcher.py
```

## First-time setup

1. Open **Settings**.
2. Set **Game Folder** to the folder that contains the mod files and `lotrbfme.exe`.
3. Click **Save**.

Settings are stored in `launcher_settings.json` in the same directory.

## Mod toggle behavior

When enabling the mod:

- `asset.dat` → `asset.safe` (if it exists)
- `asset.ros` → `asset.dat` (if it exists)
- Rename each file from `.ros` to `.big` (if present):
  - `_rosfile001`
  - `_rosfile002`
  - `_rosfile003`
  - `_rosfile004`
  - `_rosfile005`
  - `_rospatch01`
  - `_rospatch02`
  - `_rospatch03`

When disabling the mod, the launcher applies the reverse rename operations (`.big` back to `.ros`, and asset names back to their original values).
