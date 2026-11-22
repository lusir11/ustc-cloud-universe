"""Export the approved Humanities Building at its authored metre scale.

blender -b path/to/人文楼.blend -P export_replica.py [-- output.glb]
The campus places planted assets and parked vehicles as separate LOD instances.
"""
from pathlib import Path
import math
import os
import shutil
import struct
import sys
import tempfile
import zlib

import bpy
import bmesh
from mathutils import Vector
import numpy as np


def srgb(linear):
    linear = np.clip(linear, 0, 1)
    return np.where(linear <= .0031308, linear * 12.92,
                    1.055 * linear ** (1 / 2.4) - .055)


def texture(folder, name, pixels, normal=False):
    """Write bottom-up RGB samples as an embedded, explicitly color-tagged PNG."""
    data = np.uint8(np.rint(np.clip(pixels, 0, 1) * 255))[::-1].copy()
    height, width, _ = data.shape
    def chunk(kind, body):
        return (struct.pack('>I', len(body)) + kind + body
                + struct.pack('>I', zlib.crc32(kind + body)))
    path = folder / (name + '.png')
    path.write_bytes(b'\x89PNG\r\n\x1a\n'
                     + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(b''.join(b'\0' + r.tobytes() for r in data)))
                     + chunk(b'IEND', b''))
    image = bpy.data.images.load(str(path))
    if normal:
        image.colorspace_settings.name = 'Non-Color'
    image.pack()
    return image


def bake_tile(material, brick, folder, serial):
    """Tile in physical metres, matching the source's brick dimensions and palette."""
    get = lambda key: brick.inputs[key].default_value
    width, height = get('Brick Width') / get('Scale'), get('Row Height') / get('Scale')
    horizontal, vertical = (4, 8) if width / height > 2 else (3, 4)
    size = 512
    v, u = np.mgrid[:size, :size] + .5
    v *= vertical / size
    u *= horizontal / size
    row = v.astype(int)
    u += (row % 2) * brick.offset
    col = u.astype(int)
    dx = np.minimum(u % 1, 1 - u % 1) * width
    dy = np.minimum(v % 1, 1 - v % 1) * height
    mortar = get('Mortar Size') / get('Scale')
    distance = np.minimum(dx, dy)
    edge = np.clip((distance - mortar * .45) / max(.001, mortar), 0, 1)
    face = edge * edge * (3 - 2 * edge)
    rng = np.random.default_rng(1958 + serial)
    variation = rng.uniform(0, 1, (vertical, horizontal))[row, col % horizontal, None]
    first, second, joint = (np.asarray(get(k)[:3]) for k in ('Color1', 'Color2', 'Mortar'))
    masonry = (first * (1 - variation) + second * variation) * rng.normal(.98, .023, (size, size, 1))
    albedo = joint + face[:, :, None] * (masonry - joint)
    relief = face * min(.002, mortar * .45)
    slope_x = (np.roll(relief, -1, 1) - np.roll(relief, 1, 1)) * size / (2 * horizontal * width)
    slope_y = (np.roll(relief, -1, 0) - np.roll(relief, 1, 0)) * size / (2 * vertical * height)
    normals = np.stack((-slope_x, -slope_y, np.ones_like(face)), axis=-1)
    normals /= np.linalg.norm(normals, axis=-1, keepdims=True)
    label = 'humanities_surface_%02d' % serial
    tree = material.node_tree
    bs = tree.nodes.get('Principled BSDF')
    base = tree.nodes.new('ShaderNodeTexImage')
    base.image = texture(folder, label, srgb(albedo))
    tree.links.new(base.outputs['Color'], bs.inputs['Base Color'])
    detail = tree.nodes.new('ShaderNodeTexImage')
    detail.image = texture(folder, label + '_normal', normals * .5 + .5, normal=True)
    normal = tree.nodes.new('ShaderNodeNormalMap')
    tree.links.new(detail.outputs['Color'], normal.inputs['Color'])
    tree.links.new(normal.outputs['Normal'], bs.inputs['Normal'])
    return np.array([width * horizontal, height * vertical], dtype='f')


def game_glass():
    mat = bpy.data.materials.new('Humanities_Clear_Architectural_Glass')
    mat.use_nodes = True
    mat.use_backface_culling = False
    mat.surface_render_method = 'BLENDED'
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (.80, .91, .87, 1)
    bs.inputs['Metallic'].default_value = 0
    bs.inputs['Roughness'].default_value = .065
    bs.inputs['IOR'].default_value = 1.5
    bs.inputs['Alpha'].default_value = .14
    return mat


def extract_glazing(obj, groups):
    """Keep glass out of the opaque mesh and group panes by face and position.

    The renderer sorts transparent instances by depth. Putting a complete
    building's overlapping, outward-facing panes in one surface breaks sorting.
    """
    if not any(slot.material and slot.material.get('clear_architectural_glass')
               for slot in obj.material_slots):
        return
    if obj.data.users > 1:
        obj.data = obj.data.copy()
    mesh = bmesh.new()
    try:
        mesh.from_mesh(obj.data)
        slots = obj.data.materials
        panes = [f for f in mesh.faces if slots[f.material_index].get('clear_architectural_glass')]
        for face in panes:
            vertices = [obj.matrix_world @ v.co for v in face.verts]
            normal = (vertices[1]-vertices[0]).cross(vertices[2]-vertices[0]).normalized()
            axis = max(range(3), key=lambda i: abs(normal[i]))
            if normal[axis] < 0:
                normal.negate()
            center = sum(vertices, Vector()) / len(vertices)
            key = (tuple(round(q*8) for q in normal), round(normal.dot(center)),
                   math.floor(center[(axis+1)%2] / 12))
            groups.setdefault(key, []).append(vertices)
        bmesh.ops.delete(mesh, geom=panes, context='FACES')
        mesh.to_mesh(obj.data)
        obj.data.update()
    finally:
        mesh.free()


def make_glass_meshes(groups):
    result = []
    glass = game_glass()
    for i, polygons in enumerate(groups.values()):
        vertices, faces = [], []
        for polygon in polygons:
            first = len(vertices)
            vertices.extend(polygon)
            faces.append(tuple(range(first, len(vertices))))
        origin = sum(vertices, Vector()) / len(vertices)
        name = 'Glazing_%02d' % (i+1)
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata([v-origin for v in vertices], [], faces)
        mesh.materials.append(glass)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = origin
        result.append(obj)
    return result


def prepare_uv(obj, tiles):
    mesh = obj.data
    layer = mesh.uv_layers.active or mesh.uv_layers.new(name='UVMap')
    layer.name = 'UVMap'
    slots = list(mesh.materials)
    if not any(m in tiles for m in slots):
        return
    corners = len(mesh.loops)
    ids = np.empty(corners, dtype='i')
    mesh.loops.foreach_get('vertex_index', ids)
    vertex = np.empty(len(mesh.vertices) * 3, dtype='f')
    mesh.vertices.foreach_get('co', vertex)
    world = np.asarray(obj.matrix_world, dtype='f')
    positions = (vertex.reshape(-1,3) @ world[:3,:3].T + world[:3,3])[ids]
    uv = np.empty(corners * 2, dtype='f')
    layer.data.foreach_get('uv', uv)
    uv = uv.reshape(-1,2)
    faces = len(mesh.polygons)
    counts, indices = np.empty(faces, dtype='i'), np.empty(faces, dtype='i')
    mesh.polygons.foreach_get('loop_total', counts)
    mesh.polygons.foreach_get('material_index', indices)
    corner_mat = np.repeat(indices, counts)
    normal = np.empty(faces * 3, dtype='f')
    mesh.polygons.foreach_get('normal', normal)
    axis = np.repeat(np.abs(normal.reshape(-1,3) @ np.linalg.inv(world[:3,:3])).argmax(axis=1), counts)
    for slot, mat in enumerate(slots):
        mask = corner_mat == slot
        if mat in tiles:
            for k, coords in enumerate(((1,2), (0,2), (0,1))):
                surface = mask & (axis == k)
                uv[surface] = positions[surface][:,coords] / tiles[mat]
    layer.data.foreach_set('uv', uv.ravel())


def select(objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def export(output, temp):
    scene = bpy.context.scene
    geometry = [o for o in scene.objects if o.type in {'MESH','CURVE','FONT'} and not o.hide_render
                and not any('Studio' in c.name for c in o.users_collection)]
    if not any('贯通铺装' in o.name for o in geometry):
        raise ValueError('The input must be the approved open-passage building.')
    materials = {s.material for obj in geometry for s in obj.material_slots if s.material}
    tiles = {}
    for mat in sorted(materials, key=lambda m: m.name):
        brick = next((n for n in mat.node_tree.nodes if n.type == 'TEX_BRICK'), None)
        if brick:
            tiles[mat] = bake_tile(mat, brick, temp, len(tiles) + 1)
    if not any(m.get('clear_architectural_glass') for m in materials):
        raise ValueError('Choose the revision with transparent glazing before exporting.')
    for obj in geometry:
        if obj.type == 'MESH' and any(p.loop_total > 4 for p in obj.data.polygons):
            triangulate = obj.modifiers.new('Triangulate n-gons for tangent space', 'TRIANGULATE')
            triangulate.min_vertices = 5
    select(geometry)
    bpy.ops.object.convert(target='MESH')
    batches = {}
    glass_groups = {}
    for obj in sorted(bpy.context.selected_objects, key=lambda item: item.name):
        extract_glazing(obj, glass_groups)
        if not obj.data.polygons:
            continue
        prepare_uv(obj, tiles)
        batches.setdefault(obj.users_collection[0].name, []).append(obj)
    result = []
    for name, group in batches.items():
        select(group)
        bpy.ops.object.join()
        batch = bpy.context.object
        batch.name = name
        result.append(batch)
    result.extend(make_glass_meshes(glass_groups))
    select(result)
    asset = temp / 'humanities_replica.glb'
    bpy.ops.export_scene.gltf(filepath=str(asset), export_format='GLB', use_selection=True,
                              export_yup=True, export_animations=False, export_cameras=False,
                              export_lights=False, export_extras=False, export_tangents=True,
                              export_all_vertex_colors=False)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.tmp', delete=False) as staging:
        working = Path(staging.name)
    try:
        shutil.copyfile(asset, working)
        os.replace(working, output)
    finally:
        working.unlink(missing_ok=True)
    print('EXPORTED', len(result), 'batches;', output.stat().st_size, 'bytes:', output)


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    campus = Path(__file__).resolve().parents[2]
    output = Path(args[0]).resolve() if args else campus/'godot/assets/models/humanities_replica.glb'
    with tempfile.TemporaryDirectory() as folder:
        export(output, Path(folder))
