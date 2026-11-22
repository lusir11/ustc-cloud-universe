extends "res://../tools/validate_library_walkthrough.gd"

const CAMPUS_MODEL = preload("res://scripts/pe_humanities.gd")
var building: Node3D


# Asset-space east, depth and elevation are the same metre coordinates as Blender.
func site(east: float, depth: float, elevation: float = .02) -> Vector3:
	return building.to_global(Vector3(east, elevation, -depth))


func travel(label: String, target: Vector3, ticks: int) -> void:
	var start: Vector3 = player.position
	player.set_view(start, target)
	verify(label, await walk(target, ticks, false))
	if not results[label]:
		print("STOPPED ", label, " start=", start, " end=", player.position, " expected=", target)
		for i in player.get_slide_collision_count():
			print("CONTACT ", player.get_slide_collision(i).get_collider().name)


func measure(start: Vector3, end: Vector3) -> Dictionary:
	var space: PhysicsDirectSpaceState3D = game.world.get_world_3d().direct_space_state
	return space.intersect_ray(PhysicsRayQueryParameters3D.create(start, end, 0xFFFFFFFF, [player.get_rid()]))


func check_walks() -> void:
	var east_road := site(31.6, -8.0)
	var west_turn := site(31.6, 39.0)
	var south_road := site(-3.4, 39.0)
	if "--humanities-focus" in OS.get_cmdline_user_args():
		var spawn: Vector3 = player.global_position
		var facing: Vector3 = -player.orbit.global_transform.basis.z
		var to_door := site(31.6, 4.8, .1) - spawn
		to_door.y = 0
		verify("focus_starts_facing_glass_bridge",facing.normalized().dot(to_door.normalized()) > .97)
		await travel("focus_spawn_can_walk_into_passage", site(31.6, 6), 1280)
	await orient(east_road, west_turn)
	await travel("east_road_through_arcade_to_west_approach", west_turn, 1650)
	await travel("west_approach_to_south_campus_path", south_road, 1270)
	await travel("south_path_back_to_rear_entrance", west_turn, 1270)
	await travel("through_arcade_back_to_east_road", east_road, 1650)

	var gate := site(9.9, -8)
	var lobby := site(9.9, 24.0)
	await orient(gate,lobby)
	await travel("public_road_through_gate_into_courtyard", lobby, 1150)
	await travel("courtyard_lobby_back_to_road", gate, 1150)

	# The original sports north entrance remains a playable three-step annex.
	var foot := Vector3(-309.89,.05,505.60)
	var top := Vector3(-309.89,.30,508.49)
	await orient(foot,top)
	verify("north_entry_walk_up_steps",await walk(top,240,false) and player.position.y > .21)
	for i in range(3):
		var step := Vector3(-309.89,2.8,507.98+i*.32)
		var hit := measure(step, step + Vector3.DOWN*3)
		verify("north_step_height_%d" % (i+1),not hit.is_empty() and absf(hit.position.y-.1*(i+1)) < .03)
	var coach = game.hero_interactions.actors["sports"]
	var ground := measure(coach.home+Vector3.UP*.11,coach.home+Vector3.DOWN*.25)
	verify("coach_at_north_forecourt_on_ground",not ground.is_empty() and absf(ground.position.y-coach.home.y)<.06)
	var approach: Vector3 = coach.home+Vector3(-1.7,.10,.15)
	await orient(foot,approach)
	await travel("north_forecourt_to_coach",approach,240)
	verify("coach_conversation_prompt", game.hero_interactions.nearest == "sports")

	await orient(site(44, .9), site(44, 4.9))
	await travel("humanities_front_landings_walk_up", site(44, 4.9, 1.036), 320)
	verify("standing_on_seventh_step", absf(player.position.y - site(44, 4.9, 1.036).y) < .05)
	for i in 7:
		var p := site(44,1.83 + .286 * i, 2.7)
		var hit := measure(p, p + Vector3.DOWN * 3.0)
		verify("humanities_step_%d" % (i+1),not hit.is_empty() and absf(hit.position.y-(CAMPUS_MODEL.ORIGIN.y+.148*(i+1)))<.025)
	for side in [-1,1]:
		var hit := measure(site(31.6,30,1.7), site(31.6+side*6,30,1.7))
		verify("arcade_wall_%d" % side, not hit.is_empty() and hit.collider.name=="PEHumanitiesSolid"
				and absf(hit.position.distance_to(site(31.6,30,1.7))-4)<.07)
	var beam := measure(site(31.6,21.78,1.7),site(31.6,21.78,5))
	verify("inside_beam_clear_height",not beam.is_empty() and absf(beam.position.y-site(31.6,21.78,3.67).y)<.025)


func check_sightlines() -> void:
	var clear := true
	for offset in [-1.0,0.0,1.0]:
		for height in [1.0,1.8,2.6]:
			var hit := measure(site(31.6+offset,-1,height),site(31.6+offset,34.6,height))
			if not hit.is_empty():
				print("SIGHT_BLOCK ", offset, " ", height, " ", hit.collider.get_path(), " ", hit.position, " shape ", hit.shape)
				clear = false
	verify("sightline_across_both_openings", clear)


func record_views() -> void:
	# Use the active campus and its regular sunlight, neighbors, vegetation and avatar.
	for layer in game.find_children("*", "CanvasLayer", true, false):
		layer.hide()
	await orient(site(31.6,1), site(31.6,20))
	player.frozen = true
	player.set_free_camera(true)
	player.avatar.hide()
	var cam: Camera3D = player.camera
	var original_fov := cam.fov
	var views := [
		["01-front", site(32,-11,3.2), site(28.8,7.6,6.8), 70],
		["02-rear", site(31.3,43,2.55), site(31.6,30.5,3.03), 64],
		["03-arcade", site(30.6,1.7,1.69), site(31.7,18,2.04), 62],
		["05-campus", site(16,-28,37), site(31,12,6.4), 48]
	]
	for view in views:
		cam.global_position = view[1]
		cam.look_at(view[2])
		cam.fov = view[3]
		await capture_view(view[0])
	cam.fov = original_fov
	player.set_free_camera(false)
	player.frozen = false
	if not player.third_person:
		player.toggle_view()
	await orient(site(31.15,7.25),site(31.35,29))
	player.touch_move = Vector2(0,-.75)
	var origin: Vector3 = player.global_position
	await wait_physics(20)
	player.frozen = true
	player.touch_move = Vector2.ZERO
	verify("walking_avatar_moved", player.position.distance_to(origin)>.35 and player.avatar.visible)
	await capture_view("04-student-walk")


func capture_view(title: String) -> void:
	for i in 12:
		await process_frame
		await RenderingServer.frame_post_draw
	var picture := root.get_texture().get_image()
	verify("capture_" + title,picture.save_jpg(output.path_join(title+".jpg"),.94)==OK)


func run() -> void:
	if output.is_empty():
		output = ProjectSettings.globalize_path("res://../renders/pe_humanities/replica").simplify_path()
	DirAccess.make_dir_recursive_absolute(output)
	game = load("res://scenes/campus_game.tscn").instantiate()
	root.add_child(game)
	player = game.player
	player.touch_mode = true
	await wait_physics(18)
	building = game.world.get_node("PEHumanities")
	verify("campus_ready",game.game_ready)
	verify("new_asset_in_active_campus", building.scene_file_path == CAMPUS_MODEL.MODEL
		and building.position.is_equal_approx(CAMPUS_MODEL.ORIGIN))
	var capture_only := "--capture-only" in OS.get_cmdline_user_args()
	check_sightlines()
	if not capture_only:
		await check_walks()
	if DisplayServer.get_name() != "headless":
		await record_views()
	elif capture_only:
		verify("rendered_backend_required",false)
	var passed := not results.values().has(false)
	var name := "captures.json" if capture_only else "checks.json"
	var report := FileAccess.open(output.path_join(name),FileAccess.WRITE)
	report.store_string(JSON.stringify({"passed":passed, "checks":results, "source_sha256":FileAccess.get_sha256(CAMPUS_MODEL.MODEL)},"\t"))
	report.close()
	print("PE_HUMANITIES_COMPLETE ",passed)
	quit(0 if passed else 1)
