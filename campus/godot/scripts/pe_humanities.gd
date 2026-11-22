extends RefCounted

const Geometry = preload("res://scripts/north_axis_environment.gd")
const MODEL = "res://assets/models/pe_humanities.glb"
const COLLISION = "res://assets/models/pe_humanities_collision.json"
const SCOOTER = "res://assets/models/campus_scooter.glb"
const SCOOTER_DISTANT = "res://assets/models/campus_scooter_distant.glb"
const ORIGIN = Vector3(-310.0, 0.0, 530.0)

# Keep the east-west passage, north entry forecourt and narrow west facade
# strip clear of trees generated for the superseded footprints.
static func planting_allowed(tree: Dictionary) -> bool:
	var foot := Vector2(tree.position[0], tree.position[2])
	return not (Rect2(-338, 529.6, 52.0, 11.5).has_point(foot)
		or Rect2(-315.7, 501.8, 17.8, 10.4).has_point(foot)
		or Rect2(-328, 514.6, 4.0, 15.1).has_point(foot))

static func build(campus: Node3D) -> void:
	var scene: PackedScene = load(MODEL)
	var building: Node3D = scene.instantiate()
	building.name = "PEHumanities"
	building.position = ORIGIN
	campus.world.add_child(building)
	# The linear fixtures illuminate the parking bays below the two bridges.
	for x in [-319.0, -306.0, -292.5]:
		var light := OmniLight3D.new()
		light.position = Vector3(x, 3.85, 535.525) - ORIGIN
		light.light_color = Color("#ffefd8")
		light.light_energy = 1.25
		light.omni_range = 8.5
		light.omni_attenuation = 0.85
		light.distance_fade_enabled = true
		light.distance_fade_begin = 42.0
		light.distance_fade_length = 12.0
		building.add_child(light)
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(COLLISION))
	_add_parked_scooters(building, layout.parking)
	_add_gardens(building, layout.get("planting", []))
	for i in layout.solids.size():
		var solid: Dictionary = layout.solids[i]
		Geometry._solid(campus, [Geometry.polygon(solid.outline)], solid.bottom, solid.top, "PEHumanitiesSolid%d" % i)

static func _add_gardens(building: Node3D, positions: Array) -> void:
	var garden := Node3D.new()
	garden.name = "CourtyardGardens"
	building.add_child(garden)
	var plants := {}
	for site in positions:
		var kind := String(site.kind)
		if not plants.has(kind):
			plants[kind] = load("res://assets/models/humanities_%s.glb" % kind)
		var plant: Node3D = plants[kind].instantiate()
		plant.name = "%s_%02d" % [kind, garden.get_child_count() + 1]
		plant.position = Vector3(site.position[0], site.position[1], site.position[2]) - ORIGIN
		plant.rotation.y = site.rotation_y
		plant.scale = Vector3.ONE * float(site.scale)
		garden.add_child(plant)


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
		pose.position = Vector3(bay.position[0], bay.position[1], bay.position[2]) - ORIGIN
		pose.rotation.y = bay.rotation_y
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
