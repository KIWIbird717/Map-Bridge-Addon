"""
Script to build OSM Importer for blender
Check dependencies, copy files & scrips and create ready to install addon zip
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from ._addon_builder_utils import BuildError, AddonBuilderUtils, overrides


class BlenderAddonBuilder(AddonBuilderUtils):
    addon_zip_filename = "osm-importer-addon.zip"
    project_build_folder_name = "osm-importer-addon"
    __poetry_install_link = "https://python-poetry.org/docs/#installation"

    def __init__(self):
        super(BlenderAddonBuilder, self).__init__()

        self.addon_dir = self.project_root / "src"
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"

    def __log(self,  message: str, method: str | None = None):
        print(
            f"[f'{BlenderAddonBuilder.__name__}'] {f'[{method}]' if method else ''} {message}")

    def check_python_version(self):
        """Check Python version"""
        self.__log("Check Python version...",
                   method=self.check_python_version.__name__)
        version = sys.version_info
        if version.major != 3 or version.minor != 11:
            raise BuildError(
                f"Require Python 3.11.* current version: {version.major}.{version.minor}")
        self.__log(f"Python {version.major}.{version.minor}.{version.micro}",
                   method=self.check_python_version.__name__)

    def check_poetry(self):
        """Check for Poetry"""
        self.__log("Check for Poetry...", method=self.check_poetry.__name__)
        try:
            result = self._run_command(["poetry", "--version"])
            self.__log(
                f"Find Poetry: {result.stdout.strip()}", method=self.check_poetry.__name__)
        except (FileNotFoundError, BuildError):
            raise BuildError(
                f"Unable to find Poetry. Install Poetry: {self.__poetry_install_link}")

    def create_addon_package(self):
        """Create addon zip package"""
        self.__log("Create addon zip package...",
                   method=self.create_addon_package.__name__)

        # Create temporal build folder
        temp_addon_dir = self.build_dir / self.project_build_folder_name
        if temp_addon_dir.exists():
            shutil.rmtree(temp_addon_dir)

        temp_addon_dir.mkdir(parents=True, exist_ok=True)

        # Copy files from src folder
        for item in self.addon_dir.iterdir():
            dest = temp_addon_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
            self.__log(f"Copied: {item.name}",
                       method=self.create_addon_package.__name__)

        # Create ZIP archive
        zip_path = self.dist_dir / self.addon_zip_filename
        self.dist_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_addon_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_name = Path(self.project_build_folder_name) / \
                        file_path.relative_to(temp_addon_dir)
                    zipf.write(file_path, arc_name)
                    self.__log(
                        f"Add to archive: {arc_name}", method=self.create_addon_package.__name__)

        self.__log(f"Addon zip created: {zip_path}",
                   method=self.create_addon_package.__name__)
        return zip_path

    def cleanup(self):
        """Cleanup temporal files"""
        self.__log("Run cleanup temporal files...",
                   method=self.cleanup.__name__)
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.__log("Cleanup completed", method=self.cleanup.__name__)

    def build(self):
        try:
            self.__log("Run building addon", method=self.build.__name__)

            # Check for dependencies
            self.check_python_version()
            self.check_poetry()

            # Build
            self.create_addon_package()

        except BuildError as error:
            self.__log(f"Build error: {error}", method=self.build.__name__)
        except Exception as error:
            self.__log(f"Unexpected error: {error}",
                       method=self.build.__name__)
            sys.exit(1)
        finally:
            self.cleanup()


def main():
    """Build script entry point"""
    builder = BlenderAddonBuilder()
    builder.build()


if __name__ == "__main__":
    main()
