from bpy.props import FloatProperty
from bpy.types import PropertyGroup


class MapBridgeProperties(PropertyGroup):
    name = "map_bridge"

    minLng: FloatProperty(
        name="Min Lng",
        description="Min Longitude of imported aria",
        precision=6,
        min=-180.,
        max=180.,
        default=10.392798
    )
    minLat: FloatProperty(
        name="Min Lat",
        description="Min Latitude of imported aria",
        precision=6,
        min=-89.,
        max=89.,
        default=43.722474
    )
    maxLng: FloatProperty(
        name="Max Lng",
        description="Max Longitude of imported aria",
        precision=6,
        min=-180.,
        max=180.,
        default=10.396832
    )
    maxLat: FloatProperty(
        name="Min Lat",
        description="Min Latitude of imported aria",
        precision=6,
        min=-89.,
        max=89.,
        default=43.723862
    )
