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

        # google_import = scene.google_import

        # box1 = layout.box()
        # box1.label(text="Bbox coordinates")

        # # first point
        # row1 = box1.row()
        # row1.prop(google_import, "geo_coord_1", icon='PINNED')
        # # validate first point
        # if hasattr(google_import, 'geo_coord1_error') and scene["geo_coord1_error"]:
        #     row1.label(text="", icon='ERROR')
        #     box1.label(text=scene["geo_coord1_error"], icon='ERROR')

        # # second point
        # row2 = box1.row()
        # row2.prop(google_import, "geo_coord_2", icon='PINNED')
        # # Validate second point
        # if hasattr(context.scene, 'geo_coord2_error') and scene["geo_coord2_error"]:
        #     row2.label(text="", icon='ERROR')
        #     box1.label(text=scene["geo_coord2_error"], icon='ERROR')

        # # import button
        # layout.operator("google_earth.run", text="Import")
