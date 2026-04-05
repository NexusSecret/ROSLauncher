# ROSLauncher

Simple desktop launcher for toggling a game mod and launching the game executable.

## Features

- Toggle mod with one button (Enable/Disable)
- Launch `lotrbfme.exe` from the selected game folder
- Update button placeholder for future update-server integration
- Settings dialog to configure game folder
- Resolution dropdown in Settings (saved to config and synced to game options)
- Shellmap dropdown loaded from `shellmaps.json`
- Test Mode checkbox
- Matching custom art for **Enable/Disable**, **Launch Game**, and **Settings** buttons
- Optional header logo image (`ros_logo.png`)
- Right-side sample scroll display panel reserved for future hosted content
- Optional background image (`ros_bg.png`)

## Requirements

- Python 3.9+ (includes `tkinter` on most Windows installs)

## Run

```bash
python launcher.py
```

If `updatebtn.png` and `updateover.png` are placed next to `launcher.py`, the launcher uses them for the **Enable/Disable**, **Launch Game**, and **Settings** buttons with overlaid text color `#b86517`.

If `ros_logo.png` is placed next to `launcher.py`, it is shown as the launcher header. The launcher background color is `#251611`.

If `ros_bg.png` is placed next to `launcher.py`, it is used as the launcher background image.

> Note: these optional image files are intentionally gitignored so you can keep art assets local without blocking PR updates.

`news_feed.html` is included as a styled template page for hosted update/news content and now reads entries from `feed.json` (same folder/URL path).

Configured feed URLs in `launcher.py`:
- Page: `https://roslauncher.s3.ap-southeast-2.amazonaws.com/news/news_feed.html`
- JSON: `https://roslauncher.s3.ap-southeast-2.amazonaws.com/news/feed.json`

## First-time setup

1. Open **Settings**.
2. Set **Game Folder** to the folder that contains the mod files and `lotrbfme.exe`.
3. Select your preferred screen resolution from the dropdown.
4. Select your preferred shellmap (optional).
5. (Optional) Enable **Test Mode**.
6. Click **Save**.

Settings are stored in `launcher_settings.json` in the same directory.
When you save settings, the launcher also updates line 19 in:
`%APPDATA%/My Battle for Middle-Earth Files/Options.ini`
with the selected resolution.

Shellmap list entries come from `shellmaps.json` in this format:

```json
[
  { "file_name": "mtshell.ros", "display_name": "Minas Tirith" },
  { "file_name": "hdshell.ros", "display_name": "Helm's Deep" }
]
```

When selected, `file_name` is renamed from `.ros` to `_rosz<name>.big` in the game folder.
When changed/deselected, the previous `_rosz<name>.big` is renamed back to `.ros`.

News feed entries in `feed.json` support:
- `title` (string)
- `meta` (string)
- `body` (string)
- `image_url` (optional image URL)
- `image_alt` (optional alt text for image)
- `youtube_url` (optional YouTube link; rendered as embed in `news_feed.html`)

In `news_feed.html`, `body` supports newline rendering, so you can use `\n` / `\n\n` inside the JSON text for line and paragraph breaks.

Launcher note: the in-app feed panel is text-based, so image/video media are shown as clickable URLs in the launcher, while full inline media rendering is available in `news_feed.html`.

When **Test Mode** is enabled, `rostest.ros` is renamed to `_rostest.big`.
When disabled, `_rostest.big` is renamed back to `rostest.ros`.

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
