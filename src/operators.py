import bpy
import webbrowser
from bpy.types import Context
from ._types import OperatorReturnItems


class MAPBRIDGE_OT_OpenWebInterface(bpy.types.Operator):
    bl_idname = 'mapbridge.webinterface'
    bl_label = "Select"
    bl_description = "Open webinterface to select imported aria"
    __website_link = "http://localhost:5173"

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        self.report({"INFO"}, f"Open website {self.__website_link}")
        webbrowser.open(self.__website_link)
        return {'FINISHED'}


class MAPBRIDGE_OT_PasteCoordinates(bpy.types.Operator):
    bl_idname = 'mapbridge.paste'
    bl_label = 'Paste'
    bl_description = 'Paste coordinates'

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        return {'FINISHED'}
