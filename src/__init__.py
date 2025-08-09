import bpy
from typing import Type
from bpy.types import PropertyGroup
from bpy.props import PointerProperty
from bpy.utils import register_class, unregister_class

from .operators import MAPBRIDGE_OT_OpenWebInterface, MAPBRIDGE_OT_PasteCoordinates
from .osm.operator import MAPBRIDGE_OT_RunOsmImport
from .properties import MapBridgeProperties

from .google_earth.operator import MAPBRIDGE_OT_OpenEarthWebsite, MAPBRIDGE_OT_RunGoogleEarthImport
from .panel import MAPBRIDGE_PT_MainPanel

from .google_earth.register_binaries import register_binaries

bl_info = {
    "name": "Map Bridge",
    "blender": (4, 0, 0),
    "category": "Import-Export",
    "author": "KIWIbird717",
}

classes = [
    MAPBRIDGE_PT_MainPanel,
    MAPBRIDGE_OT_RunGoogleEarthImport,
    MAPBRIDGE_OT_OpenEarthWebsite,
    MAPBRIDGE_OT_RunOsmImport,
    MAPBRIDGE_OT_OpenWebInterface,
    MAPBRIDGE_OT_PasteCoordinates,
]
properties: list[Type[PropertyGroup]] = [MapBridgeProperties]

classes.extend(properties)


def register():
    register_binaries()

    # register classes
    for cls in classes:
        register_class(cls)

    # set used properties
    for prop in properties:
        setattr(bpy.types.Scene, prop.name, PointerProperty(type=prop))


def unregister():
    # unregister classes
    for cls in classes:
        unregister_class(cls)

    # delete used properties
    for prop in properties:
        delattr(bpy.types.Scene, prop.name)
