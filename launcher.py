import json
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

CONFIG_PATH = Path("launcher_settings.json")
BUTTON_NORMAL_IMAGE = Path("updatebtn.png")
BUTTON_HOVER_IMAGE = Path("updateover.png")
BUTTON_TEXT_COLOR = "#b86517"
LOGO_IMAGE = Path("ros_logo.png")
APP_BG_COLOR = "#251611"


@dataclass
class LauncherSettings:
    game_directory: str = ""

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

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Return of Shadow Launcher")
        self.root.geometry("760x430")
        self.root.configure(bg=APP_BG_COLOR)
        self.settings = LauncherSettings.load()
        self.button_images = self._load_button_images()
        self.logo_image = self._load_logo_image()

        if self.logo_image is not None:
            title = tk.Label(root, image=self.logo_image, bg=APP_BG_COLOR, pady=12)
            title.pack()
        else:
            title = tk.Label(
                root,
                text="Return of Shadow Launcher",
                font=("Segoe UI", 18, "bold"),
                fg=BUTTON_TEXT_COLOR,
                bg=APP_BG_COLOR,
                pady=12,
            )
            title.pack()

        self.toggle_button = self._create_image_button(
            text="Enable Mod",
            command=self.toggle_mod,
        )
        self.toggle_button.pack(pady=8)

        self.launch_button = self._create_image_button(
            text="Launch Game",
            command=self.launch_game,
        )
        self.launch_button.pack(pady=8)

        self.settings_button = self._create_image_button(
            text="Settings",
            command=self.open_settings,
        )
        self.settings_button.pack(pady=8)

        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(root, textvariable=self.status_var, fg="#c28d52", bg=APP_BG_COLOR)
        status.pack(pady=14)
        self.refresh_toggle_button()

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

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
        window.geometry("600x140")
        window.grab_set()

        game_directory_var = tk.StringVar(value=self.settings.game_directory)

        def add_path_row(row: int, label_text: str, var: tk.StringVar, select_file: bool = True) -> None:
            tk.Label(window, text=label_text, anchor="w").grid(row=row, column=0, padx=8, pady=8, sticky="w")
            tk.Entry(window, textvariable=var, width=60).grid(row=row, column=1, padx=8, pady=8, sticky="we")

            def browse() -> None:
                selected = filedialog.askopenfilename() if select_file else filedialog.askdirectory()
                if selected:
                    var.set(selected)

            tk.Button(window, text="Browse", command=browse).grid(row=row, column=2, padx=8, pady=8)

        add_path_row(0, "Game Folder", game_directory_var, select_file=False)

        def save_settings() -> None:
            self.settings.game_directory = game_directory_var.get().strip()
            self.settings.save()
            self.set_status("Settings saved.")
            self.refresh_toggle_button()
            window.destroy()

        tk.Button(window, text="Save", width=12, command=save_settings).grid(
            row=1,
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

    def _create_image_button(self, text: str, command) -> "ImageTextButton | tk.Button":
        if self.button_images is None:
            # Fallback for environments where image files are not present.
            return tk.Button(
                self.root,
                text=text,
                width=24,
                command=command,
                bg="#5a3016",
                fg=BUTTON_TEXT_COLOR,
                activebackground="#7a421f",
                activeforeground=BUTTON_TEXT_COLOR,
            )

        return ImageTextButton(
            self.root,
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
