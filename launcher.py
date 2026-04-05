import json
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

CONFIG_PATH = Path("launcher_settings.json")


@dataclass
class LauncherSettings:
    game_exe_path: str = ""
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
        self.root.title("Simple Mod Launcher")
        self.root.geometry("360x240")
        self.settings = LauncherSettings.load()

        title = tk.Label(
            root,
            text="Game Mod Launcher",
            font=("Segoe UI", 14, "bold"),
            pady=12,
        )
        title.pack()

        self.toggle_button = tk.Button(root, width=24, command=self.toggle_mod)
        self.toggle_button.pack(pady=6)
        tk.Button(root, text="Launch Game", width=24, command=self.launch_game).pack(pady=6)
        tk.Button(root, text="Settings", width=24, command=self.open_settings).pack(pady=6)

        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(root, textvariable=self.status_var, fg="#333")
        status.pack(pady=10)
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
        self.toggle_button.configure(text="Disable Mod" if self.mod_is_enabled() else "Enable Mod")

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
        messagebox.showinfo("Mod Enabled", f"Completed. Renamed {renamed} file(s).")

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
        messagebox.showinfo("Mod Disabled", f"Completed. Renamed {renamed} file(s).")

    def toggle_mod(self) -> None:
        if self.mod_is_enabled():
            self.disable_mod()
        else:
            self.enable_mod()

    def launch_game(self) -> None:
        exe_path = Path(self.settings.game_exe_path)

        if not self.settings.game_exe_path:
            messagebox.showerror("Missing settings", "Please configure game executable path in Settings.")
            return

        if not exe_path.exists():
            messagebox.showerror("File not found", f"Executable does not exist:\n{exe_path}")
            return

        subprocess.Popen([str(exe_path)], cwd=str(exe_path.parent))
        self.set_status("Game launched.")

    def open_settings(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("Launcher Settings")
        window.geometry("600x180")
        window.grab_set()

        game_exe_var = tk.StringVar(value=self.settings.game_exe_path)
        game_directory_var = tk.StringVar(value=self.settings.game_directory)

        def add_path_row(row: int, label_text: str, var: tk.StringVar, select_file: bool = True) -> None:
            tk.Label(window, text=label_text, anchor="w").grid(row=row, column=0, padx=8, pady=8, sticky="w")
            tk.Entry(window, textvariable=var, width=60).grid(row=row, column=1, padx=8, pady=8, sticky="we")

            def browse() -> None:
                selected = filedialog.askopenfilename() if select_file else filedialog.askdirectory()
                if selected:
                    var.set(selected)

            tk.Button(window, text="Browse", command=browse).grid(row=row, column=2, padx=8, pady=8)

        add_path_row(0, "Game EXE", game_exe_var)
        add_path_row(1, "Game Folder", game_directory_var, select_file=False)

        def save_settings() -> None:
            self.settings.game_exe_path = game_exe_var.get().strip()
            self.settings.game_directory = game_directory_var.get().strip()
            self.settings.save()
            self.set_status("Settings saved.")
            self.refresh_toggle_button()
            window.destroy()

        tk.Button(window, text="Save", width=12, command=save_settings).grid(
            row=2,
            column=2,
            padx=8,
            pady=12,
            sticky="e",
        )

        window.columnconfigure(1, weight=1)


def main() -> None:
    root = tk.Tk()
    ModLauncherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
