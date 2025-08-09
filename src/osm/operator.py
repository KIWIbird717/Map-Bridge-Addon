import bpy
from bpy.types import Context
from .._types import OperatorReturnItems


class MAPBRIDGE_OT_RunOsmImport(bpy.types.Operator):
    bl_idname = "osm.run"
    bl_label = "OSM Import"

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        return {'FINISHED'}
