import bpy
import os
import platform
import shutil
import glob
import subprocess
import webbrowser
from decimal import Context

from .._types import OperatorReturnItems
from ._utils import validate_coordinates


class MAPBRIDGE_OT_OpenEarthWebsite(bpy.types.Operator):
    bl_idname = "google_earth.website"
    bl_label = "Select"
    bl_description = "Open earth.google.com/web website to select imported aria"
    __website_link = "https://earth.google.com/web/"

    def execute(self, _context: Context) -> set[OperatorReturnItems]:
        self.report({"INFO"}, f"Open website {self.__website_link}")
        webbrowser.open(self.__website_link)
        return {'FINISHED'}


class MAPBRIDGE_OT_RunGoogleEarthImport(bpy.types.Operator):
    bl_idname = "google_earth.run"
    bl_label = "Run import"

    def get_binary_path(self, addon_dir):
        """
        Define path to binary depend of OS
        """
        system = platform.system().lower()

        if system == "darwin":
            binary_name = "earth-export-macos"
        elif system == "windows":
            binary_name = "earth-export-win.exe"
        elif system == "linux":
            binary_name = "earth-export-linux"
        else:
            raise OSError(f"Unsupported OS: {system}")

        binary_path = os.path.join(addon_dir, binary_name)

        if not os.path.exists(binary_path):
            raise FileNotFoundError(f"Binary not found: {binary_path}")

        return binary_path, system

    def format_coordinates_for_bbox(self, coord_string):
        """
        Format coordinates to --bbox style
        """
        formatted = coord_string.replace(' ', ':')
        return formatted

    def create_bbox_string(self, coord1, coord2, system):
        """
        Create --bbox string from 2 coordinates
        """
        formatted_coord1 = self.format_coordinates_for_bbox(coord1)
        formatted_coord2 = self.format_coordinates_for_bbox(coord2)

        if system == "darwin":
            return f"--bbox={formatted_coord1};{formatted_coord2}"
        elif system == "windows":
            return f"--bbox=\"{formatted_coord1};{formatted_coord2}\""
        elif system == "linux":
            return f"--bbox={formatted_coord1};{formatted_coord2}"
        else:
            raise OSError(f"Unsupported OS: {system}")

    def find_latest_model(self, obj_dir):
        """
        Found the latest created model.sc.obj file with formatted model
        """
        date_folders = glob.glob(os.path.join(obj_dir, "*-*-*T*-*-*.*"))

        if not date_folders:
            return None

        # Sort by creation date (take the latest)
        date_folders.sort(key=lambda x: os.path.getctime(x))
        latest_folder = date_folders[-1]

        model_path = os.path.join(latest_folder, "model.sc.obj")

        if os.path.exists(model_path):
            return model_path

        return None

    def cleanup_cache(self, obj_dir):
        """
        Clear cache folder
        """
        try:
            if os.path.exists(obj_dir):
                shutil.rmtree(obj_dir)
                os.makedirs(obj_dir, exist_ok=True)
        except Exception as e:
            print(f"Exception while cleaning cache folder: {e}")

    def execute(self, context):
        # Validate coordinates
        coord1_valid, coord1_error = validate_coordinates(
            context.scene.geo_coord1)
        coord2_valid, coord2_error = validate_coordinates(
            context.scene.geo_coord2)

        if not coord1_valid:
            self.report({'ERROR'}, f"Error in first point: {coord1_error}")
            return {'CANCELLED'}

        if not coord2_valid:
            self.report({'ERROR'}, f"Error in second point: {coord2_error}")
            return {'CANCELLED'}

        addon_dir = os.path.dirname(__file__)

        try:
            binary_path, system = self.get_binary_path(addon_dir)
        except (OSError, FileNotFoundError) as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        # Create temporary folder for export
        home_dir = os.path.expanduser("~")
        temp_export_dir = os.path.join(home_dir, ".google-earth-export")
        obj_dir = os.path.join(temp_export_dir, "downloaded_files", "obj")

        os.makedirs(obj_dir, exist_ok=True)

        self.cleanup_cache(obj_dir)

        # Create --bbox string
        bbox_string = self.create_bbox_string(
            context.scene.geo_coord1, context.scene.geo_coord2, system)
        self.report({'INFO'}, f"Запуск скрипта с аргументом: {bbox_string}")

        # Run binary
        try:
            self.report({'INFO'}, f"Run export... {binary_path}")

            process = subprocess.Popen(
                [binary_path, bbox_string],
                cwd=temp_export_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Read console logs
            for line in process.stdout:
                line = line.strip()
                if line:
                    print(f"EXPORT: {line}")

                    if "done. saved as" in line:
                        break

            # Wait till process ends
            awaited_process = process.wait()
            self.report({'INFO'}, f"awaited_process: {awaited_process}")

        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"Error in run binary: {e}")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Unexpected error: {e}")
            return {'CANCELLED'}

        # Found created model
        model_path = self.find_latest_model(obj_dir)
        self.report({'INFO'}, f"model_path: {model_path}")

        if not model_path:
            self.report({'ERROR'}, "Model not found after export")
            return {'CANCELLED'}

        # Import model into Blender
        try:
            bpy.ops.wm.obj_import(filepath=model_path)

            # Setup textures
            for texture in bpy.data.textures:
                texture.extension = 'EXTEND'

            self.report(
                {'INFO'}, f"Model {model_path} imported: {os.path.basename(model_path)}")

        except Exception as e:
            self.report({'ERROR'}, f"Error importing model: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}
