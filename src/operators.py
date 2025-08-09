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
        try:
            # 1. Получаем строку из буфера обмена
            clipboard_text = context.window_manager.clipboard.strip()

            # 2. Разделяем по запятым и убираем лишние пробелы
            coords = [c.strip() for c in clipboard_text.split(",")]

            if len(coords) != 4:
                self.report(
                    {"ERROR"}, "Invalid format! Expected: minLat,minLng,maxLat,maxLng")
                return {'CANCELLED'}

            # 3. Преобразуем в float
            minLat, minLng, maxLat, maxLng = map(float, coords)

            # 4. Записываем в свойства аддона
            map_bridge = context.scene.map_bridge
            map_bridge.minLat = minLat
            map_bridge.minLng = minLng
            map_bridge.maxLat = maxLat
            map_bridge.maxLng = maxLng

            self.report({"INFO"}, "Coordinates pasted successfully")
            return {'FINISHED'}

        except ValueError:
            self.report({"ERROR"}, "Could not parse coordinates as float")
            return {'CANCELLED'}
