extends RefCounted

const Geometry = preload("res://scripts/north_axis_environment.gd")
const Surfaces = preload("res://scripts/road_surfaces.gd")
const MODEL = "res://assets/models/humanities_replica.glb"
const COLLISION = "res://assets/models/humanities_replica_layout.json"
const SCOOTER = "res://assets/models/campus_scooter.glb"
const SCOOTER_DISTANT = "res://assets/models/campus_scooter_distant.glb"
const ORIGIN = Vector3(-280.0, .125, 567.125)

# The courtyard, through passage and its two approaches have authored planting.
static func planting_allowed(tree: Dictionary) -> bool:
	var foot := Vector2(tree.position[0], tree.position[2])
	return not (Rect2(-316, 503.8, 38.5, 64.8).has_point(foot)
		or Rect2(-321.8, 532.7, 7.8, 37.3).has_point(foot)
		or Rect2(-279.5, 554.5, 6.8, 6.0).has_point(foot)
		or Rect2(-315.7, 501.8, 17.8, 10.4).has_point(foot)
		or Rect2(-328, 514.6, 4.0, 15.1).has_point(foot))

static func build(campus: Node3D) -> void:
	var scene: PackedScene = load(MODEL)
	var building: Node3D = scene.instantiate()
	building.name = "PEHumanities"
	building.position = ORIGIN
	building.rotation.y = PI / 2.0
	campus.world.add_child(building)
	_apply_clear_glazing(building)
	for z in [-9.8, -20.9, -30.2]:
		var light := OmniLight3D.new()
		light.position = Vector3(31.6, 3.68, z)
		light.light_color = Color("#ffefd8")
		light.light_energy = 1.25
		light.light_specular = .06
		light.omni_range = 8.5
		light.omni_attenuation = 0.85
		light.distance_fade_enabled = true
		light.distance_fade_begin = 42.0
		light.distance_fade_length = 12.0
		building.add_child(light)
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(COLLISION))
	_add_parked_scooters(building, layout.parking)
	_add_gardens(campus, building, layout.planting)
	_add_collisions(building, layout.solids)
	_add_paths(campus)
	preload("res://scripts/pe_humanities_annex.gd").build(campus)

static func _apply_clear_glazing(building: Node3D) -> void:
	var glass := ShaderMaterial.new()
	glass.shader = preload("res://shaders/humanities_glass.gdshader")
	for panel: MeshInstance3D in building.find_children("Glazing_*", "MeshInstance3D", true, false):
		# Dedicated pane meshes leave masonry and the glazing bars in the shadow pass.
		panel.material_override = glass
		panel.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

static func _vector(values: Array) -> Vector3:
	return Vector3(values[0], values[1], values[2])

static func _pose(site: Dictionary) -> Transform3D:
	var basis := Basis(Vector3.UP, site.rotation_y) * Basis.from_scale(_vector(site.scale))
	return Transform3D(basis, _vector(site.position))

static func _add_collisions(building: Node3D, solids: Array) -> void:
	var body := StaticBody3D.new()
	body.name = "PEHumanitiesSolid"
	building.add_child(body)
	for solid in solids:
		var collider := CollisionShape3D.new()
		if solid.kind == "cylinder":
			var cylinder := CylinderShape3D.new()
			cylinder.height = solid.height
			cylinder.radius = solid.radius
			collider.shape = cylinder
		else:
			var box := BoxShape3D.new()
			box.size = _vector(solid.size)
			collider.shape = box
		collider.position = _vector(solid.position)
		collider.rotation.y = solid.get("rotation_y", 0.0)
		body.add_child(collider)

static func _add_paths(campus: Node3D) -> void:
	# Join the courtyard to the east sidewalk and the rear opening to the south footpath.
	var paths := [
		[[-279.0,555.1],[-273.3,555.1],[-273.3,559.5],[-279.0,559.5]],
		[[-314.32,533.53],[-320.5,533.53],[-320.5,569.2],[-317.5,569.2],
		 [-317.5,537.52],[-314.32,537.52]]
	]
	for coords in paths:
		var part := [Geometry.polygon(coords)]
		Geometry._surface(campus, part, .12, Surfaces.material(campus, "pavers"), "HumanitiesApproach")
		Geometry._solid(campus, part, -.10, .12, "HumanitiesWalkableApproach")

static func _add_gardens(campus: Node3D, building: Node3D, positions: Array) -> void:
	var garden := Node3D.new()
	garden.name = "CourtyardGardens"
	building.add_child(garden)
	# Keep nearby plants in instanced batches so the renderer can cull each bed
	# and select its mesh LOD without submitting a separate draw per shrub.
	var groups := {}
	for site in positions:
		var kind := String(site.kind)
		var pose := _pose(site)
		var bed := Vector2i(floori(pose.origin.x / 12), floori(pose.origin.z / 12))
		if not groups.has(kind):
			groups[kind] = {}
		if not groups[kind].has(bed):
			groups[kind][bed] = []
		groups[kind][bed].append(pose)
	for kind in groups:
		var scene: PackedScene = load("res://assets/models/humanities_%s.glb" % kind)
		var plant: Node3D = scene.instantiate()
		var parts := []
		campus.asset_parts(plant, Transform3D.IDENTITY, parts)
		plant.free()
		for part in parts:
			for poses: Array in groups[kind].values():
				var batch := MultiMesh.new()
				batch.transform_format = MultiMesh.TRANSFORM_3D
				batch.mesh = part.mesh
				batch.instance_count = poses.size()
				for i in poses.size():
					batch.set_instance_transform(i, poses[i] * part.transform)
				var instance := MultiMeshInstance3D.new()
				instance.name = kind
				instance.multimesh = batch
				instance.lod_bias = .45
				instance.visibility_range_end = 190.0
				instance.visibility_range_end_margin = 12.0
				garden.add_child(instance, true)


static func _add_parked_scooters(building: Node3D, bays: Array) -> void:
	var close: PackedScene = load(SCOOTER)
	var distant: PackedScene = load(SCOOTER_DISTANT)
	var parking := Node3D.new()
	parking.name = "ParkedScooters"
	building.add_child(parking)
	for i in bays.size():
		var bay: Dictionary = bays[i]
		var pose := Node3D.new()
		pose.name = "Bay%02d" % (i + 1)
		pose.transform = _pose(bay)
		parking.add_child(pose)
		var detailed: Node3D = close.instantiate()
		var simplified: Node3D = distant.instantiate()
		simplified.position.y = -.037
		pose.add_child(detailed)
		pose.add_child(simplified)
		for instance in [detailed, simplified]:
			var meshes = instance.find_children("*", "MeshInstance3D", true, false)
			if instance is MeshInstance3D:
				meshes.append(instance)
			for mesh: MeshInstance3D in meshes:
				if instance == detailed:
					mesh.visibility_range_end = 38
					mesh.visibility_range_end_margin = 1
				else:
					mesh.visibility_range_begin = 38
					mesh.visibility_range_begin_margin = 1
					mesh.visibility_range_end = 150
