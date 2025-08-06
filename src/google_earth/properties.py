from bpy.types import PropertyGroup, Context
from bpy.props import StringProperty

from ._utils import validate_coordinates


def update_coord1(self, context: Context):
    """Обновление при изменении первой координаты"""
    scene = context.scene
    if not scene:
        return
    is_valid, error_msg = validate_coordinates(self.geo_coord1)
    if is_valid:
        scene["geo_coord1_error"] = ""
    else:
        scene["geo_coord1_error"] = error_msg


def update_coord2(self, context: Context):
    """Обновление при изменении второй координаты"""
    scene = context.scene
    if not scene:
        return
    is_valid, error_msg = validate_coordinates(self.geo_coord2)
    if is_valid:
        scene["geo_coord2_error"] = ""
    else:
        scene["geo_coord2_error"] = error_msg


class GoogleImportProperties(PropertyGroup):
    name = "google_import"

    geo_coord_1: StringProperty(
        name="Coordinate 1",
        description='Format: 43°43\'25"N 10°23\'49"E',
        update=update_coord1
    )

    geo_coord_2: StringProperty(
        name="Coordinate 2",
        description='Format: 43°43\'25"N 10°23\'49"E',
        update=update_coord2
    )
