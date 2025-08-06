import bpy
import stat
from pathlib import Path
from bpy.app import binary_path
from bpy.types import PropertyGroup, PointerProperty
from bpy.utils import register_class, unregister_class
from typing import Type

from .google_earth.register_binaries import register_binaries

bl_info = {
    "name": "Map Bridge",
    "blender": (4, 0, 0),
    "category": "Import-Export",
    "author": "KIWIbird717",
    "support": "TESTING"
}

classes = []
properties: list[Type[PropertyGroup]] = []


def register():
    register_binaries()

    # register classes
    for cls in classes:
        register_class(cls)

    # set used properties
    for prop in properties:
        scene = bpy.types.Scene
        setattr(scene, prop.name, PointerProperty(type=prop))


def unregister():
    # unregister classes
    for cls in classes:
        unregister_class(cls)

    # delete used properties
    for prop in properties:
        scene = bpy.types.Scene
        delattr(scene, prop.name)
