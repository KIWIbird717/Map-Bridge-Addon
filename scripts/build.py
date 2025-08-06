import os
import sys
import shutil
import zipfile
from pathlib import Path
from ._addon_builder_utils import BuildError, AddonBuilderUtils


class PreBuildCheck(AddonBuilderUtils):
    """
    Check for necessary tools to build the project
    """

    def __init__(self):
        super().__init__()
        self.google_earth_exporter_dir = self.project_root / "google-earth-exporter"

    def __log(self,  message: str, method: str | None = None):
        print(
            f"[{PreBuildCheck.__name__}] {f'[{method}]' if method else ''} {message}")

    def check_python_version(self):
        self.__log("Check Python version...",
                   method=self.check_python_version.__name__)
        version = sys.version_info
        if version.major != 3 or version.minor != 11:
            raise BuildError(
                f"Require Python 3.11.* current version: {version.major}.{version.minor}")
        self.__log(f"Python {version.major}.{version.minor}.{version.micro}",
                   method=self.check_python_version.__name__)

    def check_poetry(self):
        self.__log("Check for Poetry...", method=self.check_poetry.__name__)
        try:
            result = self._run_command(["poetry", "--version"])
            self.__log(
                f"Find Poetry: {result.stdout.strip()}", method=self.check_poetry.__name__)
        except (FileNotFoundError, BuildError):
            raise BuildError(
                "Unable to find Poetry. Install Poetry: https://python-poetry.org/docs/#installation")

    def check_nodejs(self):
        self.__log("Check for Node.js...")
        try:
            result = self._run_command(["node", "--version"])
            version_str = result.stdout.strip().lstrip('v')
            major_version = int(version_str.split('.')[0])

            if major_version < 18:
                raise BuildError(
                    f"Require Node.js 18+, current version: {version_str}")

            self.__log(f"✓ Node.js {version_str}")
        except (FileNotFoundError, BuildError):
            raise BuildError(
                "Node.js not found. Install Node.js 18+: https://nodejs.org/")

    def check_npm(self):
        self.__log("Check for npm...")
        try:
            result = self._run_command(["npm", "--version"])
            self.__log(f"✓ npm {result.stdout.strip()}")
        except (FileNotFoundError, BuildError):
            raise BuildError("npm not found. Install Node.js with npm")

    def check_git(self):
        self.__log("Check for Git...")
        try:
            result = self._run_command(["git", "--version"])
            self.__log(f"✓ {result.stdout.strip()}")
        except (FileNotFoundError, BuildError):
            raise BuildError(
                "Git not found. Install Git: https://git-scm.com/")

    def setup_submodule(self):
        """
        Checks and configures the submodule
        """
        self.__log("Check for google-earth-exporter submodule...")

        if not self.google_earth_exporter_dir.exists():
            self.__log("Submodule not found, initialize...")
            self._run_command(["git", "submodule", "init"])
            self._run_command(["git", "submodule", "update"])
        else:
            self.__log("Submodule has been found, updating...")
            self._run_command(["git", "submodule", "update", "--remote"])

        if not self.google_earth_exporter_dir.exists():
            raise BuildError(
                "Unable to initialize google-earth-exporter submodule")

        self.__log("Submodule initialized")

    def install_node_dependencies(self):
        """
        Install Node.js dependencies
        """
        self.__log("Installing Node.js dependencies...")

        package_json = self.google_earth_exporter_dir / "package.json"
        if not package_json.exists():
            raise BuildError("package.json not found in google-earth-exporter")

        self._run_command(["npm", "install"],
                          cwd=self.google_earth_exporter_dir)
        self.__log("Node.js dependencies installed")


class BlenderAddonBuilder(PreBuildCheck):
    addon_zip_filename = "map-bridge.zip"
    project_build_folder_name = "map-bridge"
    __poetry_install_link = "https://python-poetry.org/docs/#installation"

    def __init__(self):
        super().__init__()
        self.addon_dir = self.project_root / "src"
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"

    def __log(self,  message: str, method: str | None = None):
        print(
            f"[{BlenderAddonBuilder.__name__}] {f'[{method}]' if method else ''} {message}")

    def is_binaries_builded(self) -> tuple[bool, str | None]:
        """
        Validate if binaries already builded
        """
        build_dir = self.google_earth_exporter_dir / "build"
        expected_binaries = [
            "earth-export-win.exe",
            "earth-export-macos",
            "earth-export-linux"
        ]

        for binary in expected_binaries:
            binary_path = build_dir / binary
            if not binary_path.exists():
                return False, binary

        return True, None

    def build_binaries(self):
        """
        Build binaries from google-earth-exporter submodule
        """
        self.__log('Check for created binaries')
        is_builded, _ = self.is_binaries_builded()
        if is_builded:
            return self.__log("Binaries already builded")

        self.__log("Build binaries...")

        # Validate for pkg script in package.json
        package_json = self.google_earth_exporter_dir / "package.json"
        if not package_json.exists():
            raise BuildError("package.json not found")

        # run binaries build
        self._run_command(["npm", "run", "pkg"],
                          cwd=self.google_earth_exporter_dir)

        # Validate if binaries are builded
        is_builded, binary = self.is_binaries_builded()
        if not is_builded:
            raise BuildError(f"Binary file not found: {binary}")

        self.__log("Binaries builded")

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

        # Copy binary files to google_earth folder
        source_build_dir = self.google_earth_exporter_dir / "build"
        for binary in source_build_dir.glob("*"):
            if binary.is_file():
                dst_binary = temp_addon_dir / "google_earth" / binary.name
                shutil.copy2(binary, dst_binary)
                self.__log(f"Copy binary: {binary.name}")

        # Create ZIP archive
        zip_path = self.dist_dir / self.addon_zip_filename
        self.dist_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_addon_dir):
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
            self.check_nodejs()
            self.check_npm()
            self.check_git()

            # Project setup
            self.setup_submodule()
            self.install_node_dependencies()

            # Build project
            self.build_binaries()
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
