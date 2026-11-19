extends RefCounted

const Geometry = preload("res://scripts/north_axis_environment.gd")
const MODEL = "res://assets/models/pe_humanities.glb"
const COLLISION = "res://assets/models/pe_humanities_collision.json"
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
	for i in layout.solids.size():
		var solid: Dictionary = layout.solids[i]
		Geometry._solid(campus, [Geometry.polygon(solid.outline)], solid.bottom, solid.top, "PEHumanitiesSolid%d" % i)
