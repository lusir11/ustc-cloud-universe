extends Node3D

const STUDENT_MODEL: PackedScene = preload("res://assets/campus_student.glb")
const MOVEMENT = preload("res://scripts/player.gd")

var locomotion: StringName = &"idle"
var animator: AnimationPlayer
var skeleton: Skeleton3D


func _ready() -> void:
	var model: Node3D = STUDENT_MODEL.instantiate()
	model.rotation.y = PI # glTF character front is +Z; the player moves toward -Z.
	add_child(model)
	# glTF COLOR_0 multiplies base color. The scene importer can leave this off
	# even when the skinned mesh contains the painted skin tones.
	for instance: MeshInstance3D in model.find_children("*", "MeshInstance3D", true, false):
		var mesh := instance.mesh as ArrayMesh
		for surface in mesh.get_surface_count():
			var material := mesh.surface_get_material(surface) as StandardMaterial3D
			if material and mesh.surface_get_format(surface) & Mesh.ARRAY_FORMAT_COLOR:
				material.vertex_color_use_as_albedo = true
	skeleton = model.find_children("*", "Skeleton3D", true, false)[0]
	animator = model.find_children("*", "AnimationPlayer", true, false)[0]
	animator.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	for clip in [&"idle", &"walk", &"run"]:
		animator.get_animation(clip).loop_mode = Animation.LOOP_LINEAR
	animator.play(locomotion)
	animator.advance(0.0)


func animate(speed: float, vertical: float, grounded: bool, dt: float) -> void:
	var next: StringName = &"idle"
	var rate := 1.0
	if not grounded:
		next = &"jump" if vertical > 0.0 else &"fall"
	elif speed > (MOVEMENT.WALK_SPEED + MOVEMENT.RUN_SPEED) * 0.5:
		next = &"run"
		rate = clampf(speed / MOVEMENT.RUN_SPEED, 0.7, 1.25)
	elif speed > 0.12:
		next = &"walk"
		rate = clampf(speed / MOVEMENT.WALK_SPEED, 0.55, 1.3)

	if next != locomotion:
		locomotion = next
		animator.play(next, 0.13)
	animator.speed_scale = rate
	animator.advance(dt)
