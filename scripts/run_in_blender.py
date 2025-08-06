import platform
import json
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Optional
from .build import BlenderAddonBuilder


class BlenderAddonInstaller(BlenderAddonBuilder):
    custom_blender_path: str | None = None

    def __init__(self):
        super(BlenderAddonInstaller, self).__init__()

        self.addon_zip_path = self.dist_dir / BlenderAddonBuilder.addon_zip_filename
        self.config_file = self.project_root / "blender_config.json"

        # Default Blender paths for different OS
        self.default_blender_paths = {
            "darwin": [
                "/Applications/Blender.app/Contents/MacOS/Blender",
                "/Applications/Blender.app/Contents/Resources/Blender.app/Contents/MacOS/Blender"
            ],
            "linux": [
                "/usr/bin/blender",
                "/usr/local/bin/blender",
                "/opt/blender/blender"
            ],
            "win32": [
                "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
                "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe",
                "C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe"
            ]
        }

    def __log(self,  message: str, method: str | None = None):
        print(
            f"[f'{BlenderAddonInstaller.__name__}'] {f'[{method}]' if method else ''} {message}")

    def get_blender_path(self) -> Optional[Path]:
        """Acquire Blender path from default variable \"self.custom_blender_path\" or find path automatically"""
        # If custom blender path declared
        if self.custom_blender_path:
            return Path(self.custom_blender_path)

        # Automatically find Blender path
        system = platform.system().lower()
        if system == "darwin":
            system_key = "darwin"
        elif system == "linux":
            system_key = "linux"
        else:
            system_key = "win32"

        for path in self.default_blender_paths.get(system_key, []):
            if Path(path).exists():
                return Path(path)

        return None

    def save_blender_path(self, blender_path: Path):
        """
        Save path to Blender to config file
        """
        config = {"blender_path": str(blender_path)}
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def find_blender_interactively(self) -> Path:
        """Interactive Blender search"""
        self.__log("Blender not found automatically.",
                   method=self.find_blender_interactively.__name__)
        self.__log("Please provide the path to the Blender executable file:",
                   method=self.find_blender_interactively.__name__)

        while True:
            path_input = input("Blender path: ").strip()
            if not path_input:
                continue

            blender_path = Path(path_input)
            if blender_path.exists():
                self.save_blender_path(blender_path)
                return blender_path
            else:
                self.__log(
                    f"File not found: {blender_path}", method=self.find_blender_interactively.__name__)
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    sys.exit(1)

    def check_addon_exists(self) -> bool:
        """Validate builded addon zip"""
        if not self.addon_zip_path.exists():
            self.__log(f"Адон не найден: {self.addon_zip_path}",
                       method=self.check_addon_exists.__name__)
            self.__log("Сначала выполните сборку: make build",
                       method=self.check_addon_exists.__name__)
            return False
        return True

    def get_blender_addons_dir(self, _: Path) -> Path:
        """Get Blender addons directory path"""
        system = platform.system().lower()

        if system == "darwin":
            # macOS
            home = Path.home()
            return home / "Library" / "Application Support" / "Blender" / "4.0" / "scripts" / "addons"
        elif system == "linux":
            # Linux
            home = Path.home()
            return home / ".config" / "blender" / "scripts" / "addons"
        else:
            # Windows
            home = Path.home()
            return home / "AppData" / "Roaming" / "Blender Foundation" / "Blender" / "scripts" / "addons"

    def install_addon(self, blender_path: Path):
        """Install addon into Blender"""
        self.__log(
            f"Installing addon {self.project_build_folder_name}...", method=self.install_addon.__name__)

        # Получаем директорию адонов
        addons_dir = self.get_blender_addons_dir(blender_path)
        addons_dir.mkdir(parents=True, exist_ok=True)

        # Распаковываем адон
        addon_name = self.project_build_folder_name
        addon_dir = addons_dir / addon_name

        # Удаляем старую версию если есть
        if addon_dir.exists():
            shutil.rmtree(addon_dir)

        # Распаковываем новый адон
        with zipfile.ZipFile(self.addon_zip_path, 'r') as zip_ref:
            zip_ref.extractall(addons_dir)

        self.__log(
            f"✓ Адон установлен в: {addon_dir}", method=self.install_addon.__name__)

    def enable_addon_in_blender(self, blender_path: Path):
        """Adding addon to Blender"""
        self.__log("Adding addon to Blender...",
                   method=self.enable_addon_in_blender.__name__)

        # Создаем временный Python скрипт для включения адона
        enable_script = self.project_root / "temp_enable_addon.py"

        script_content = f'''
        import bpy
        import addon_utils

        # Turing addon on
        addon_name = {self.project_build_folder_name}
        if not addon_utils.check(addon_name)[1]:
            bpy.ops.preferences.addon_enable(module=addon_name)
            print(f"Адон {{addon_name}} включен")
        else:
            print(f"Адон {{addon_name}} уже включен")

        # Сохраняем настройки
        bpy.ops.wm.save_userpref()
        print("Настройки сохранены")
        '''

        with open(enable_script, 'w', encoding='utf-8') as f:
            f.write(script_content)

        try:
            # Запускаем Blender с Python скриптом
            subprocess.run([
                str(blender_path),
                "--background",
                "--python", str(enable_script)
            ], check=True)

            self.__log("Addon added to Blender",
                       method=self.enable_addon_in_blender.__name__)
        finally:
            # Удаляем временный скрипт
            if enable_script.exists():
                enable_script.unlink()

    def launch_blender(self, blender_path: Path):
        self.__log("Launch Blender...", method=self.launch_blender.__name__)

        try:
            subprocess.Popen([str(blender_path)])
            self.__log("Blender running", method=self.launch_blender.__name__)
        except subprocess.SubprocessError as error:
            self.__log(f"Error while launching Blender: {error}")

    def install_and_launch(self):
        """Install addon and launch Blender app"""
        self.__log("Start installing Blender addon...",
                   method=self.install_and_launch.__name__)

        if not self.check_addon_exists():
            return

        # Acquire Blender executable path
        blender_path = self.get_blender_path()
        if not blender_path:
            blender_path = self.find_blender_interactively()

        self.__log(f"Blender found: {blender_path}",
                   method=self.install_and_launch.__name__)

        self.install_addon(blender_path)
        self.enable_addon_in_blender(blender_path)
        self.launch_blender(blender_path)

        self.__log("Install completed! Blender launched with installed addon",
                   method=self.install_and_launch.__name__)

    def run(self):
        try:
            self.install_and_launch()
        except KeyboardInterrupt:
            self.__log("Installation was interrupted by the user",
                       method=self.run.__name__)
        except Exception as e:
            self.__log(f"Error: {e}", method=self.run.__name__)
            sys.exit(1)


def main():
    """Runner script entry point"""
    installer = BlenderAddonInstaller()
    installer.run()


if __name__ == "__main__":
    main()
