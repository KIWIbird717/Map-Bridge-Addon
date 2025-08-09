import bpy
from bpy.types import Context


class MAPBRIDGE_PT_MainPanel(bpy.types.Panel):
    bl_label = "Map Bridge"
    bl_idname = "MAPBRIDGE_PT_MainPanel"
    bl_region_type = "WINDOW"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "Map Bridge"

    def draw(self, context: Context) -> None:
        layout = self.layout
        scene = context.scene
        if not layout or not scene:
            return

        map_bridge = scene.map_bridge

        box = layout.box()
        row = box.row()
        row.label(text="Aria Selection")

        row = box.row(align=True)
        row.operator("mapbridge.webinterface")
        row.operator("mapbridge.paste")

        box.label(text="Manual Selection")
        split = box.split(factor=0.25)
        split.label(text="")
        split.split(factor=0.67).prop(map_bridge, "maxLat")
        row = box.row()
        row.prop(map_bridge, "minLng")
        row.prop(map_bridge, "maxLng")
        split = box.split(factor=0.25)
        split.label(text="")
        split.split(factor=0.67).prop(map_bridge, "minLat")

        col = layout.column(align=True)
        col.label(text="Choose import method")
        col.operator("osm.run")
        col.operator("google_earth.run")
