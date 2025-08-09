import xml.etree.ElementTree as ET
import tempfile
import bpy
import os
import urllib.request
import math
import numpy as np

from bpy.types import Context
from .._types import OperatorReturnItems


OSM_API_URL = "https://api.openstreetmap.org/api/0.6/map?bbox={min_lon},{min_lat},{max_lon},{max_lat}"


class MAPBRIDGE_OT_RunOsmImport(bpy.types.Operator):
    bl_idname = "osm.run"
    bl_label = "Import OSM Area"
    bl_description = "Import 3D buildings, roads and sidewalks from OpenStreetMap for the selected area"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        scene = context.scene
        if not scene:
            return {'CANCELLED'}

        map_bridge = scene.map_bridge
        min_lat = map_bridge.minLat
        max_lat = map_bridge.maxLat
        min_lon = map_bridge.minLng
        max_lon = map_bridge.maxLng

        # Calculate center point for coordinate conversion
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2

        url = OSM_API_URL.format(
            min_lon=min_lon, min_lat=min_lat, max_lon=max_lon, max_lat=max_lat)
        self.report({"INFO"}, f"Downloading OSM data from: {url}")

        # Download OSM data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".osm") as tmpfile:
            try:
                with urllib.request.urlopen(url) as response:
                    tmpfile.write(response.read())
                tmpfile_path = tmpfile.name
            except Exception as e:
                self.report({"ERROR"}, f"Failed to download OSM data: {e}")
                return {'CANCELLED'}

        # Parse OSM XML
        try:
            tree = ET.parse(tmpfile_path)
            root = tree.getroot()
        except Exception as e:
            self.report({"ERROR"}, f"Failed to parse OSM XML: {e}")
            os.remove(tmpfile_path)
            return {'CANCELLED'}

        # Extract nodes
        nodes = {}
        for node in root.findall('node'):
            node_id = node.attrib['id']
            lat = float(node.attrib['lat'])
            lon = float(node.attrib['lon'])
            nodes[node_id] = (lat, lon)

        # Helper: lat/lon to local XY
        earth_radius = 6378137

        def latlon_to_xy(lat, lon):
            x = (lon - center_lon) * (math.pi / 180) * \
                earth_radius * math.cos(math.radians(center_lat))
            y = (lat - center_lat) * (math.pi / 180) * earth_radius
            return (x, y)

        # Highway type to width mapping
        highway_widths = {
            'motorway': 10.0,
            'motorway_link': 10.0,
            'trunk': 8.0,
            'trunk_link': 8.0,
            'primary': 7.0,
            'primary_link': 7.0,
            'secondary': 6.0,
            'secondary_link': 6.0,
            'tertiary': 5.0,
            'tertiary_link': 5.0,
            'unclassified': 4.0,
            'residential': 4.0,
            'living_street': 4.0,
            'service': 3.0,
            'pedestrian': 3.0,
            'track': 3.0,
            'footway': 1.5,
            'path': 1.5,
            'sidewalk': 1.5
        }
        default_width = 2.0
        road_height = 0.1

        # Parse ways: buildings, roads and sidewalks
        buildings = []
        roads = []
        sidewalks = []
        road_types = []

        for way in root.findall('way'):
            tags = {tag.attrib['k']: tag.attrib['v']
                    for tag in way.findall('tag')}
            nds = [nd.attrib['ref'] for nd in way.findall('nd')]

            if 'building' in tags and tags['building'] != 'no':
                buildings.append(nds)
            elif 'highway' in tags:
                roads.append(nds)
                road_types.append(tags['highway'])
            elif tags.get('footway') == 'sidewalk':
                sidewalks.append(nds)

        # Create buildings
        building_count = 0
        for nds in buildings:
            verts = []
            for ref in nds:
                if ref in nodes:
                    lat, lon = nodes[ref]
                    x, y = latlon_to_xy(lat, lon)
                    verts.append((x, y, 0))
            if len(verts) < 3:
                continue

            mesh = bpy.data.meshes.new("OSM_Building")
            mesh.from_pydata(verts, [], [list(range(len(verts)))])
            mesh.update()
            obj = bpy.data.objects.new("OSM_Building", mesh)
            context.collection.objects.link(obj)

            # Extrude for 3D effect
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.extrude_region_move(
                TRANSFORM_OT_translate={"value": (0, 0, 10)})
            bpy.ops.object.mode_set(mode='OBJECT')
            building_count += 1

        # Create roads
        road_count = 0
        for nds, htype in zip(roads, road_types):
            verts = []
            for ref in nds:
                if ref in nodes:
                    lat, lon = nodes[ref]
                    x, y = latlon_to_xy(lat, lon)
                    verts.append((x, y))
            if len(verts) < 2:
                continue

            width = highway_widths.get(htype, default_width)
            half_w = width / 2.0

            # Build offset points for left/right edge
            left = []
            right = []
            for i in range(len(verts)):
                if i == 0:
                    dir_vec = np.array(verts[1]) - np.array(verts[0])
                elif i == len(verts) - 1:
                    dir_vec = np.array(verts[-1]) - np.array(verts[-2])
                else:
                    dir_vec = np.array(verts[i+1]) - np.array(verts[i-1])
                dir_vec = dir_vec / np.linalg.norm(dir_vec)
                normal = np.array([-dir_vec[1], dir_vec[0]])
                lpt = np.array(verts[i]) + normal * half_w
                rpt = np.array(verts[i]) - normal * half_w
                left.append((lpt[0], lpt[1], road_height))
                right.append((rpt[0], rpt[1], road_height))

            mesh_verts = left + right
            n = len(verts)
            mesh_faces = []
            # Create faces (quads)
            for i in range(n-1):
                mesh_faces.append([i, i+1, n+i+1, n+i])

            mesh = bpy.data.meshes.new(f'OSM_Road_{htype}')
            mesh.from_pydata(mesh_verts, [], mesh_faces)
            mesh.update()
            obj = bpy.data.objects.new(f'OSM_Road_{htype}', mesh)
            context.collection.objects.link(obj)
            road_count += 1

        # Create sidewalks
        sidewalk_count = 0
        for nds in sidewalks:
            verts = []
            for ref in nds:
                if ref in nodes:
                    lat, lon = nodes[ref]
                    x, y = latlon_to_xy(lat, lon)
                    verts.append((x, y, 0.0))
            if len(verts) < 2:
                continue

            width = highway_widths['sidewalk']
            curve_data = bpy.data.curves.new('OSM_Sidewalk', type='CURVE')
            curve_data.dimensions = '3D'
            polyline = curve_data.splines.new('POLY')
            polyline.points.add(len(verts)-1)
            for i, v in enumerate(verts):
                polyline.points[i].co = (v[0], v[1], v[2], 1)
            curve_obj = bpy.data.objects.new('OSM_Sidewalk', curve_data)
            context.collection.objects.link(curve_obj)
            curve_data.bevel_depth = width / 2.0
            curve_data.bevel_resolution = 1
            sidewalk_count += 1

        os.remove(tmpfile_path)
        self.report({"INFO"},
                    f"Imported {building_count} buildings, {road_count} roads, and {sidewalk_count} sidewalks.")
        return {'FINISHED'}
