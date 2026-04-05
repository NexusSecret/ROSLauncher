import json
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

CONFIG_PATH = Path("launcher_settings.json")


@dataclass
class LauncherSettings:
    game_exe_path: str = ""
    mod_disabled_path: str = ""
    mod_enabled_path: str = ""

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

        tk.Button(root, text="Enable Mod", width=24, command=self.enable_mod).pack(pady=6)
        tk.Button(root, text="Disable Mod", width=24, command=self.disable_mod).pack(pady=6)
        tk.Button(root, text="Launch Game", width=24, command=self.launch_game).pack(pady=6)
        tk.Button(root, text="Settings", width=24, command=self.open_settings).pack(pady=6)

        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(root, textvariable=self.status_var, fg="#333")
        status.pack(pady=10)

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _move_file(self, source_str: str, destination_str: str, action: str) -> None:
        source = Path(source_str)
        destination = Path(destination_str)

        if not source_str or not destination_str:
            messagebox.showerror("Missing settings", "Please configure mod file paths in Settings.")
            return

        if not source.exists():
            messagebox.showerror("File not found", f"Source file does not exist:\n{source}")
            return

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        self.set_status(f"Mod {action}.")
        messagebox.showinfo("Success", f"Mod {action} successfully.")

    def enable_mod(self) -> None:
        self._move_file(
            self.settings.mod_disabled_path,
            self.settings.mod_enabled_path,
            "enabled",
        )

    def disable_mod(self) -> None:
        self._move_file(
            self.settings.mod_enabled_path,
            self.settings.mod_disabled_path,
            "disabled",
        )

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
        window.geometry("600x220")
        window.grab_set()

        game_exe_var = tk.StringVar(value=self.settings.game_exe_path)
        mod_disabled_var = tk.StringVar(value=self.settings.mod_disabled_path)
        mod_enabled_var = tk.StringVar(value=self.settings.mod_enabled_path)

        def add_path_row(row: int, label_text: str, var: tk.StringVar, select_file: bool = True) -> None:
            tk.Label(window, text=label_text, anchor="w").grid(row=row, column=0, padx=8, pady=8, sticky="w")
            tk.Entry(window, textvariable=var, width=60).grid(row=row, column=1, padx=8, pady=8, sticky="we")

            def browse() -> None:
                selected = filedialog.askopenfilename() if select_file else filedialog.askdirectory()
                if selected:
                    var.set(selected)

            tk.Button(window, text="Browse", command=browse).grid(row=row, column=2, padx=8, pady=8)

        add_path_row(0, "Game EXE", game_exe_var)
        add_path_row(1, "Mod Disabled File", mod_disabled_var)
        add_path_row(2, "Mod Enabled File", mod_enabled_var)

        def save_settings() -> None:
            self.settings.game_exe_path = game_exe_var.get().strip()
            self.settings.mod_disabled_path = mod_disabled_var.get().strip()
            self.settings.mod_enabled_path = mod_enabled_var.get().strip()
            self.settings.save()
            self.set_status("Settings saved.")
            window.destroy()

        tk.Button(window, text="Save", width=12, command=save_settings).grid(
            row=3,
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
