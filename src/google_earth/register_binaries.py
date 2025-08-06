import stat
from pathlib import Path


BINARIES = [
    "earth-export-win.exe",
    "earth-export-macos",
    "earth-export-linux",
]


def register_binaries() -> None:
    """
    Make binaries executable
    """
    addon_dir = Path(__file__).parent
    for bin_name in BINARIES:
        bin_path = addon_dir / bin_name
        if bin_path.exists():
            current = bin_path.stat().st_mode
            bin_path.chmod(current | stat.S_IXUSR |
                           stat.S_IXGRP | stat.S_IXOTH)
