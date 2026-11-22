extends RefCounted

const Geometry = preload("res://scripts/north_axis_environment.gd")
const MODEL = "res://assets/models/pe_north_annex.glb"
const COLLISION = "res://assets/models/pe_north_annex_collision.json"

static func build(campus: Node3D) -> void:
	var scene: PackedScene = load(MODEL)
	var annex: Node3D = scene.instantiate()
	annex.name = "SportsNorthAnnex"
	annex.position = Vector3(-310.0, 0.0, 530.0)
	campus.world.add_child(annex)
	var solids: Array = JSON.parse_string(FileAccess.get_file_as_string(COLLISION))
	for i in solids.size():
		var solid: Dictionary = solids[i]
		Geometry._solid(campus, [Geometry.polygon(solid.outline)], solid.bottom, solid.top, "SportsNorthAnnexSolid%d" % i)
