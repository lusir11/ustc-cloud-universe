"""Export local Godot colliders and placements from the open humanities replica.

blender -b path/to/人文楼.blend --python-exit-code 1 -P export_replica_layout.py
"""
import json
from math import isclose
from pathlib import Path

import bpy
from mathutils import Vector


DEST = Path(__file__).resolve().parents[2] / "godot/assets/models/humanities_replica_layout.json"


def xyz(x, y, z):
    return [round(x, 5), round(z, 5), round(-y, 5)]


def bounds(points):
    axes = list(zip(*points))
    return tuple(min(values) for values in axes) + tuple(max(values) for values in axes)


def object_bounds(obj):
    return bounds(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)


def box(solids, bounds_xyz):
    x, y, z, X, Y, Z = bounds_xyz
    solids.append({
        "kind": "box", "position": xyz((x+X)/2, (y+Y)/2, (z+Z)/2),
        "size": [round(X-x, 5), round(Z-z, 5), round(Y-y, 5)], "rotation_y": 0,
    })


def cylinder(solids, x, y, bottom, height, radius):
    solids.append({"kind": "cylinder", "position": xyz(x, y, bottom+height/2),
                   "height": round(height, 5), "radius": round(radius, 5)})


def facade_boxes(obj):
    # The building shell stores each masonry prism as bottom, top, then sides.
    mesh = obj.data
    for face in mesh.polygons:
        if face.normal.z > -.9999 or face.loop_total != 4:
            continue
        cap = mesh.polygons[face.index + 1]
        if cap.normal.z < .9999 or cap.loop_total != 4:
            continue
        bottom = [mesh.vertices[i].co for i in face.vertices]
        top = [mesh.vertices[i].co for i in cap.vertices]
        if {(v.x, v.y) for v in bottom} == {(v.x, v.y) for v in top}:
            yield mesh.materials[face.material_index].name, bounds(bottom + top)


def building_colliders(scene):
    solids = []
    # The roof slab of each enclosed wing describes its ground footprint. The
    # central roof slab instead starts at the passage ceiling. The front bridge
    # has its own separate slab and the opening above it is kept open as well.
    roofs = scene.collection.children["屋面 | 铺装、收边与机电"]
    roof_footprints = (
        "徽章翼 · 上人屋面", "东翼 · 上人屋面", "中央翼 · 上人屋面", "西翼 · 步道覆顶",
        "庭院北厅 · 西平台", "庭院北厅 · 北平台", "庭院北厅 · 玻璃大厅主屋面", "庭院北厅 · 入口翼屋面",
    )
    for name in roof_footprints:
        obj = roofs.objects[name]
        # The first face belongs to the rectangular deck, inset 18 mm from the wall.
        x, y, _, X, Y, z = bounds(obj.data.vertices[i].co for i in obj.data.polygons[0].vertices)
        base = 4.04 if name.startswith("中央翼") else -.05
        box(solids, (x-.018, y-.018, base, X+.018, Y+.018, z+.025))

    drum = scene.objects["弧形教学楼 · 砖墩、金属窗与曲面幕墙"]
    x, y, z, X, Y, Z = object_bounds(drum)
    cylinder(solids, (x+X)/2, (y+Y)/2, z, Z-z, (X-x)/2-.06)

    # Distinct objects for paving and planters carry their actual mesh limits.
    for obj in scene.collection.children["05 · 广场与花池 | Stonework"].objects:
        if "种植土" not in obj.name:
            box(solids, object_bounds(obj))
    for obj in scene.collection.children["07 · 架空通道 | Bicycle parking"].objects:
        if obj.type == "MESH" and obj.name.startswith("廊尽端"):
            box(solids, object_bounds(obj))
    entrance = scene.collection.children["入口标识 · 门廊 · 玻璃连桥"]
    for obj in entrance.objects:
        if obj.name.endswith("根砖柱") or obj.name in (
            "廊架 · 方柱", "廊架 · 临街檐梁", "红砖门框 · 侧墙柱", "庭院大厅 · 入口门槛",
            "红砖门框 · 跨街横梁",
        ):
            # Entry components batch disconnected rectangular solids in groups of eight corners.
            verts = obj.data.vertices
            assert len(verts) % 8 == 0, obj.name
            for start in range(0, len(verts), 8):
                box(solids, bounds(obj.matrix_world @ verts[j].co for j in range(start, start+8)))
    x, y, z, X, Y, _ = object_bounds(entrance.objects["连桥 · 承重楼板"])
    bridge_top = object_bounds(entrance.objects["连桥 · 顶部钢梁"])[5]
    box(solids, (x, y, z, X, Y, bridge_top))

    for material, limits in facade_boxes(scene.objects["主楼 · 四面带进深窗洞的砖墙"]):
        x, y, z, X, Y, Z = limits
        if (material.endswith("Warm grey concrete") and x >= 27.58 and X <= 35.62
                and Z <= 4.12 and (z < .01 or z > 3.85)):
            # Structural posts, overhead transverse beams and the rear lintel.
            box(solids, limits)
    for material, limits in facade_boxes(scene.objects["南立面 · 六开间与入口楼梯"]):
        x, y, z, X, Y, Z = limits
        if material.endswith("Sandblasted limestone") and isclose(Z-z, .148, abs_tol=.001):
            box(solids, limits)
        elif material.endswith("Ivory architectural precast") and y < 4 and Z > 4.8:
            box(solids, limits)
    return solids


def placements(scene, solids):
    parking, plants = [], []
    surface = object_bounds(scene.objects["桥廊前区与贯通铺装"])[5]
    for obj in scene.objects:
        if obj.instance_type != "COLLECTION" or not obj.instance_collection:
            continue
        source = obj.instance_collection
        origin, rotation, scale = obj.matrix_world.decompose()
        origin -= obj.matrix_world.to_3x3() @ source.instance_offset
        ax, ay, yaw = rotation.to_euler()
        assert max(abs(ax), abs(ay)) < 1e-5, obj.name
        x, y, z = origin
        sx, sy, sz = scale
        kind = source.name.removeprefix("原型 · ")
        if kind == "校园电单车":
            z = surface  # Align wheel contact, 7 mm below the studio instance origin.
        site = {"position": xyz(x, y, z), "rotation_y": round(yaw, 7),
                "scale": [round(sx, 5), round(sz, 5), round(sy, 5)]}
        if kind == "校园电单车":
            parking.append(site)
            solids.append({"kind": "box", "rotation_y": site["rotation_y"],
                           "position": xyz(x, y, z+.46*sz),
                           "size": [round(1.60*sx, 5), round(.92*sz, 5), round(.50*sy, 5)]})
        else:
            assert kind in ("entrance_pot", "ornamental", "background_tree", "courtyard_shrub"), kind
            plants.append({"kind": kind, **site})
            # Leaves and overhanging branches stay soft. These dimensions match the
            # physical pot or trunk, not the full spread of the foliage.
            hard_parts = {"entrance_pot": (.166, .34), "ornamental": (.074, 1.1),
                          "background_tree": (.17, 2.4)}
            if kind in hard_parts:
                r, h = hard_parts[kind]
                cylinder(solids, x, y, z, h*sz, r*min(sx, sy))
    if not parking or not plants:
        raise ValueError("The linked parking and planting collections are missing.")
    return parking, plants


if __name__ == "__main__":
    scene = bpy.context.scene
    solids = building_colliders(scene)
    parking, plants = placements(scene, solids)
    layout = {"solids": solids, "parking": parking, "planting": plants}
    DEST.write_text(json.dumps(layout, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Exported {len(solids)} collision shapes, {len(parking)} scooters, {len(plants)} plants.")
