import json
import os
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog, messagebox

CONFIG_PATH = Path("launcher_settings.json")
SHELLMAPS_PATH = Path("shellmaps.json")
BUTTON_NORMAL_IMAGE = Path("updatebtn.png")
BUTTON_HOVER_IMAGE = Path("updateover.png")
BUTTON_TEXT_COLOR = "#b86517"
LOGO_IMAGE = Path("ros_logo.png")
BG_IMAGE = Path("ros_bg.png")
APP_BG_COLOR = "#251611"


@dataclass
class LauncherSettings:
    game_directory: str = ""
    resolution: str = "1920x1080"
    shellmap_file: str = ""
    test_mode: bool = False

    @classmethod
    def load(cls) -> "LauncherSettings":
        if not CONFIG_PATH.exists():
            return cls()

        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return cls(**data)
        except Exception:
            # Fallback to defaults if config file is invalid.
            return cls()

    def save(self) -> None:
        CONFIG_PATH.write_text(
            json.dumps(asdict(self), indent=2),
            encoding="utf-8",
        )


class ModLauncherApp:
    ROS_FILES = [
        "_rosfile001",
        "_rosfile002",
        "_rosfile003",
        "_rosfile004",
        "_rosfile005",
        "_rospatch01",
        "_rospatch02",
        "_rospatch03",
    ]
    RESOLUTIONS = [
        "1280x720",
        "1366x768",
        "1600x900",
        "1920x1080",
        "2560x1440",
        "3840x2160",
    ]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Return of Shadow Launcher")
        self.root.geometry("980x520")
        self.settings = LauncherSettings.load()
        self.shellmaps = self._load_shellmaps()
        self.button_images = self._load_button_images()
        self.logo_image = self._load_logo_image()
        self.bg_image = self._load_background_image()
        self.root.configure(bg=APP_BG_COLOR)

        width = self.bg_image.width() if self.bg_image is not None else 980
        height = self.bg_image.height() if self.bg_image is not None else 520
        self.root.geometry(f"{width}x{height}")

        self.main_canvas = tk.Canvas(
            root,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0,
            bg=APP_BG_COLOR,
        )
        self.main_canvas.pack(fill="both", expand=True)

        if self.bg_image is not None:
            self.main_canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        if self.logo_image is not None:
            self.main_canvas.create_image(width // 2, 18, image=self.logo_image, anchor="n")
        else:
            self.main_canvas.create_text(
                width // 2,
                40,
                text="Return of Shadow Launcher",
                font=("Segoe UI", 18, "bold"),
                fill=BUTTON_TEXT_COLOR,
            )

        self.toggle_button = self._create_image_button(
            parent=self.main_canvas,
            text="Enable Mod",
            command=self.toggle_mod,
        )
        self.main_canvas.create_window(36, 170, window=self.toggle_button, anchor="nw")

        self.launch_button = self._create_image_button(
            parent=self.main_canvas,
            text="Launch Game",
            command=self.launch_game,
        )
        self.main_canvas.create_window(36, 240, window=self.launch_button, anchor="nw")

        self.settings_button = self._create_image_button(
            parent=self.main_canvas,
            text="Settings",
            command=self.open_settings,
        )
        self.main_canvas.create_window(36, 310, window=self.settings_button, anchor="nw")

        display_panel = tk.Frame(self.main_canvas, bg="#140d09", bd=1, relief="sunken")
        self.main_canvas.create_window(280, 170, window=display_panel, anchor="nw", width=660, height=300)

        display_title = tk.Label(
            display_panel,
            text="News / Updates (Sample)",
            bg="#140d09",
            fg=BUTTON_TEXT_COLOR,
            font=("Segoe UI", 12, "bold"),
            pady=8,
        )
        display_title.pack(anchor="w", padx=10)

        self.display_box = scrolledtext.ScrolledText(
            display_panel,
            wrap="word",
            font=("Segoe UI", 10),
            bg="#1a100c",
            fg="#e6d6b9",
            insertbackground="#e6d6b9",
            relief="flat",
            padx=10,
            pady=10,
        )
        self.display_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.display_box.insert(
            "1.0",
            "Sample Update Feed\n\n"
            "Welcome to Return of Shadow Launcher.\n\n"
            "This panel is reserved for your upcoming web-driven display feature.\n"
            "Once you provide the hosted URL, this area can be replaced with live content.\n\n"
            "- Sample item 1: Patch notes preview\n"
            "- Sample item 2: Community announcement\n"
            "- Sample item 3: Version status",
        )
        self.display_box.configure(state="disabled")

        self.status_text_item = self.main_canvas.create_text(
            36,
            height - 26,
            anchor="w",
            text="Ready",
            fill="#c28d52",
            font=("Segoe UI", 10, "bold"),
        )
        self.refresh_toggle_button()

    def set_status(self, text: str) -> None:
        self.main_canvas.itemconfigure(self.status_text_item, text=text)

    def _get_game_directory(self) -> Path | None:
        if not self.settings.game_directory:
            messagebox.showerror("Missing settings", "Please configure game directory in Settings.")
            return

        game_dir = Path(self.settings.game_directory)
        if not game_dir.exists():
            messagebox.showerror("Folder not found", f"Game directory does not exist:\n{game_dir}")
            return

        return game_dir

    def refresh_toggle_button(self) -> None:
        button_text = "Disable Mod" if self.mod_is_enabled() else "Enable Mod"
        if isinstance(self.toggle_button, ImageTextButton):
            self.toggle_button.set_text(button_text)
        else:
            self.toggle_button.configure(text=button_text)

    def mod_is_enabled(self) -> bool:
        game_dir = Path(self.settings.game_directory) if self.settings.game_directory else None
        if not game_dir or not game_dir.exists():
            return False

        return any((game_dir / f"{name}.big").exists() for name in self.ROS_FILES)

    def _rename_if_exists(self, source: Path, destination: Path) -> bool:
        if not source.exists():
            return False
        source.rename(destination)
        return True

    def enable_mod(self) -> None:
        game_dir = self._get_game_directory()
        if game_dir is None:
            return

        renamed = 0
        if self._rename_if_exists(game_dir / "asset.dat", game_dir / "asset.safe"):
            renamed += 1
        if self._rename_if_exists(game_dir / "asset.ros", game_dir / "asset.dat"):
            renamed += 1

        for name in self.ROS_FILES:
            if self._rename_if_exists(game_dir / f"{name}.ros", game_dir / f"{name}.big"):
                renamed += 1

        self.refresh_toggle_button()
        self.set_status(f"Mod enabled ({renamed} file(s) renamed).")

    def disable_mod(self) -> None:
        game_dir = self._get_game_directory()
        if game_dir is None:
            return

        renamed = 0
        if self._rename_if_exists(game_dir / "asset.dat", game_dir / "asset.ros"):
            renamed += 1
        if self._rename_if_exists(game_dir / "asset.safe", game_dir / "asset.dat"):
            renamed += 1

        for name in self.ROS_FILES:
            if self._rename_if_exists(game_dir / f"{name}.big", game_dir / f"{name}.ros"):
                renamed += 1

        self.refresh_toggle_button()
        self.set_status(f"Mod disabled ({renamed} file(s) renamed).")

    def toggle_mod(self) -> None:
        if self.mod_is_enabled():
            self.disable_mod()
        else:
            self.enable_mod()

    def launch_game(self) -> None:
        game_dir = self._get_game_directory()
        if game_dir is None:
            return

        exe_path = game_dir / "lotrbfme.exe"
        if not exe_path.exists():
            messagebox.showerror("File not found", f"Executable does not exist:\n{exe_path}")
            return

        subprocess.Popen([str(exe_path)], cwd=str(exe_path.parent))
        self.set_status("Game launched.")

    def open_settings(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("Launcher Settings")
        window.geometry("600x270")
        window.configure(bg=APP_BG_COLOR)
        window.grab_set()

        game_directory_var = tk.StringVar(value=self.settings.game_directory)
        resolution_var = tk.StringVar(value=self.settings.resolution)
        shellmap_names = ["None"] + [entry["display_name"] for entry in self.shellmaps]
        selected_shellmap_name = self._display_name_for_file(self.settings.shellmap_file) or "None"
        shellmap_var = tk.StringVar(value=selected_shellmap_name)
        test_mode_var = tk.BooleanVar(value=self.settings.test_mode)
        if resolution_var.get() not in self.RESOLUTIONS:
            resolution_var.set(self.RESOLUTIONS[0])

        def add_path_row(row: int, label_text: str, var: tk.StringVar, select_file: bool = True) -> None:
            tk.Label(window, text=label_text, anchor="w", bg=APP_BG_COLOR, fg=BUTTON_TEXT_COLOR).grid(
                row=row, column=0, padx=8, pady=8, sticky="w"
            )
            tk.Entry(
                window,
                textvariable=var,
                width=60,
                bg="#1a100c",
                fg="#e6d6b9",
                insertbackground="#e6d6b9",
                relief="flat",
            ).grid(row=row, column=1, padx=8, pady=8, sticky="we")

            def browse() -> None:
                selected = filedialog.askopenfilename() if select_file else filedialog.askdirectory()
                if selected:
                    var.set(selected)

            tk.Button(
                window,
                text="Browse",
                command=browse,
                bg="#5a3016",
                fg=BUTTON_TEXT_COLOR,
                activebackground="#7a421f",
                activeforeground=BUTTON_TEXT_COLOR,
                relief="flat",
            ).grid(row=row, column=2, padx=8, pady=8)

        add_path_row(0, "Game Folder", game_directory_var, select_file=False)

        tk.Label(window, text="Resolution", anchor="w", bg=APP_BG_COLOR, fg=BUTTON_TEXT_COLOR).grid(
            row=1, column=0, padx=8, pady=8, sticky="w"
        )
        resolution_dropdown = tk.OptionMenu(window, resolution_var, *self.RESOLUTIONS)
        resolution_dropdown.config(
            width=20,
            bg="#5a3016",
            fg=BUTTON_TEXT_COLOR,
            activebackground="#7a421f",
            activeforeground=BUTTON_TEXT_COLOR,
            highlightthickness=0,
        )
        resolution_dropdown["menu"].config(bg="#5a3016", fg=BUTTON_TEXT_COLOR)
        resolution_dropdown.grid(row=1, column=1, padx=8, pady=8, sticky="w")

        tk.Label(window, text="Shellmap", anchor="w", bg=APP_BG_COLOR, fg=BUTTON_TEXT_COLOR).grid(
            row=2, column=0, padx=8, pady=8, sticky="w"
        )
        shellmap_dropdown = tk.OptionMenu(window, shellmap_var, *shellmap_names)
        shellmap_dropdown.config(
            width=20,
            bg="#5a3016",
            fg=BUTTON_TEXT_COLOR,
            activebackground="#7a421f",
            activeforeground=BUTTON_TEXT_COLOR,
            highlightthickness=0,
        )
        shellmap_dropdown["menu"].config(bg="#5a3016", fg=BUTTON_TEXT_COLOR)
        shellmap_dropdown.grid(row=2, column=1, padx=8, pady=8, sticky="w")

        test_mode_checkbox = tk.Checkbutton(
            window,
            text="Test Mode (rostest.ros → _rostest.big)",
            variable=test_mode_var,
            bg=APP_BG_COLOR,
            fg=BUTTON_TEXT_COLOR,
            selectcolor="#1a100c",
            activebackground=APP_BG_COLOR,
            activeforeground=BUTTON_TEXT_COLOR,
        )
        test_mode_checkbox.grid(row=3, column=0, columnspan=2, padx=8, pady=8, sticky="w")

        def save_settings() -> None:
            previous_shellmap = self.settings.shellmap_file
            previous_test_mode = self.settings.test_mode
            self.settings.game_directory = game_directory_var.get().strip()
            self.settings.resolution = resolution_var.get().strip()
            selected_name = shellmap_var.get().strip()
            self.settings.shellmap_file = self._file_for_display_name(selected_name) if selected_name != "None" else ""
            self.settings.test_mode = test_mode_var.get()
            self.settings.save()
            self._apply_resolution_to_options()
            self._apply_shellmap_selection(previous_shellmap, self.settings.shellmap_file)
            self._apply_test_mode(previous_test_mode, self.settings.test_mode)
            self.set_status("Settings saved.")
            self.refresh_toggle_button()
            window.destroy()

        tk.Button(
            window,
            text="Save",
            width=12,
            command=save_settings,
            bg="#5a3016",
            fg=BUTTON_TEXT_COLOR,
            activebackground="#7a421f",
            activeforeground=BUTTON_TEXT_COLOR,
            relief="flat",
        ).grid(
            row=4,
            column=2,
            padx=8,
            pady=12,
            sticky="e",
        )

        window.columnconfigure(1, weight=1)

    def _load_button_images(self) -> dict[str, tk.PhotoImage] | None:
        if not BUTTON_NORMAL_IMAGE.exists() or not BUTTON_HOVER_IMAGE.exists():
            return None

        return {
            "normal": tk.PhotoImage(file=str(BUTTON_NORMAL_IMAGE)),
            "hover": tk.PhotoImage(file=str(BUTTON_HOVER_IMAGE)),
        }

    def _create_image_button(self, parent: tk.Widget, text: str, command) -> "ImageTextButton | tk.Button":
        if self.button_images is None:
            # Fallback for environments where image files are not present.
            return tk.Button(
                parent,
                text=text,
                width=24,
                command=command,
                bg="#5a3016",
                fg=BUTTON_TEXT_COLOR,
                activebackground="#7a421f",
                activeforeground=BUTTON_TEXT_COLOR,
            )

        return ImageTextButton(
            parent,
            text=text,
            normal_image=self.button_images["normal"],
            hover_image=self.button_images["hover"],
            command=command,
            text_color=BUTTON_TEXT_COLOR,
        )

    def _load_logo_image(self) -> tk.PhotoImage | None:
        if not LOGO_IMAGE.exists():
            return None
        image = tk.PhotoImage(file=str(LOGO_IMAGE))
        max_width = 560
        max_height = 150
        width_scale = max(1, -(-image.width() // max_width))
        height_scale = max(1, -(-image.height() // max_height))
        scale = max(width_scale, height_scale)
        if scale > 1:
            image = image.subsample(scale, scale)
        return image

    def _load_background_image(self) -> tk.PhotoImage | None:
        if not BG_IMAGE.exists():
            return None
        return tk.PhotoImage(file=str(BG_IMAGE))

    def _apply_resolution_to_options(self) -> None:
        appdata = os.getenv("APPDATA")
        if appdata:
            options_path = Path(appdata) / "My Battle for Middle-Earth Files" / "Options.ini"
        else:
            options_path = Path.home() / "AppData" / "Roaming" / "My Battle for Middle-Earth Files" / "Options.ini"

        options_path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        if options_path.exists():
            lines = options_path.read_text(encoding="utf-8", errors="ignore").splitlines()

        while len(lines) < 19:
            lines.append("")

        width, height = self.settings.resolution.split("x", maxsplit=1)
        lines[18] = f"Resolution = {width} {height}"
        options_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _load_shellmaps(self) -> list[dict[str, str]]:
        if not SHELLMAPS_PATH.exists():
            return []

        try:
            data = json.loads(SHELLMAPS_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []

        if not isinstance(data, list):
            return []

        clean_entries = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            file_name = str(entry.get("file_name", "")).strip()
            display_name = str(entry.get("display_name", "")).strip()
            if file_name and display_name:
                clean_entries.append({"file_name": file_name, "display_name": display_name})
        return clean_entries

    def _display_name_for_file(self, file_name: str) -> str:
        for entry in self.shellmaps:
            if entry["file_name"] == file_name:
                return entry["display_name"]
        return ""

    def _file_for_display_name(self, display_name: str) -> str:
        for entry in self.shellmaps:
            if entry["display_name"] == display_name:
                return entry["file_name"]
        return ""

    def _shellmap_target_big_name(self, file_name: str) -> str:
        stem = Path(file_name).stem
        return f"_rosz{stem}.big"

    def _apply_shellmap_selection(self, previous_file: str, selected_file: str) -> None:
        game_dir = self._get_game_directory()
        if game_dir is None:
            return

        if previous_file and previous_file != selected_file:
            previous_big = game_dir / self._shellmap_target_big_name(previous_file)
            previous_ros = game_dir / previous_file
            if previous_big.exists():
                previous_big.rename(previous_ros)

        if selected_file:
            selected_ros = game_dir / selected_file
            selected_big = game_dir / self._shellmap_target_big_name(selected_file)
            if selected_ros.exists():
                selected_ros.rename(selected_big)

    def _apply_test_mode(self, previous_enabled: bool, selected_enabled: bool) -> None:
        game_dir = self._get_game_directory()
        if game_dir is None:
            return

        source_ros = game_dir / "rostest.ros"
        target_big = game_dir / "_rostest.big"

        if selected_enabled and not previous_enabled:
            if source_ros.exists():
                source_ros.rename(target_big)
        elif previous_enabled and not selected_enabled:
            if target_big.exists():
                target_big.rename(source_ros)


class ImageTextButton(tk.Canvas):
    def __init__(
        self,
        master,
        text: str,
        normal_image: tk.PhotoImage,
        hover_image: tk.PhotoImage,
        command,
        text_color: str,
    ) -> None:
        self.normal_image = normal_image
        self.hover_image = hover_image
        self.command = command

        super().__init__(
            master,
            width=self.normal_image.width(),
            height=self.normal_image.height(),
            highlightthickness=0,
            bd=0,
            bg=master.cget("bg"),
        )

        self.image_item = self.create_image(0, 0, image=self.normal_image, anchor="nw")
        self.text_item = self.create_text(
            self.normal_image.width() // 2,
            self.normal_image.height() // 2,
            text=text,
            fill=text_color,
            font=("Segoe UI", 11, "bold"),
        )

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def set_text(self, text: str) -> None:
        self.itemconfigure(self.text_item, text=text)

    def _on_enter(self, _event) -> None:
        self.itemconfigure(self.image_item, image=self.hover_image)

    def _on_leave(self, _event) -> None:
        self.itemconfigure(self.image_item, image=self.normal_image)

    def _on_click(self, _event) -> None:
        self.command()


def main() -> None:
    root = tk.Tk()
    ModLauncherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
