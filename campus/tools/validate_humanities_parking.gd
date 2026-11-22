extends SceneTree

const District = preload("res://scripts/pe_humanities.gd")

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var music := root.get_node_or_null("CampusMusic") as AudioStreamPlayer
	if music:
		music.stop()
	var host = load("res://scripts/campus.gd").new()
	host.world = Node3D.new()
	root.add_child(host.world)
	host.setup_materials()
	District.build(host)
	var parking = host.world.get_node_or_null("PEHumanities/ParkedScooters")
	if not parking or parking.get_child_count() != 16:
		push_error("Expected two rows of eight occupied parking bays.")
		quit(1)
		return
	var detail_mesh_ids := {}
	var distant_mesh_ids := {}
	for index: int in parking.get_child_count():
		var bay: Node3D = parking.get_child(index)
		var side := floori(index / 8.0)
		var j := index % 8
		var bx := 28.57 if side == 0 else 34.50
		bx += (1 if side == 0 else -1) * (j * .105 + .06 * sin(j))
		var expected := Vector3(bx, .002, -(5.75 + j * 1.5 + side * .15))
		if not bay.position.is_equal_approx(expected):
			push_error("Parked scooter misplaced: " + str(bay.name))
			quit(1)
			return
		if bay.get_child_count() != 2:
			push_error("Missing near or far representation in " + str(bay.name))
			quit(1)
			return
		for i in 2:
			var model = bay.get_child(i)
			var meshes = model.find_children("*", "MeshInstance3D", true, false)
			if model is MeshInstance3D:
				meshes.append(model)
			if meshes.is_empty():
				push_error("Empty scooter geometry.")
				quit(1)
				return
			for mesh: MeshInstance3D in meshes:
				if i == 0:
					if not detail_mesh_ids.has(mesh.mesh.get_instance_id()):
						for surface in mesh.mesh.get_surface_count():
							var finish := mesh.get_active_material(surface) as BaseMaterial3D
							if finish and "enamel" in finish.resource_name.to_lower():
								if not finish.vertex_color_use_as_albedo and finish.albedo_color.is_equal_approx(Color.WHITE):
									push_error("Missing mint or ivory paint on imported enamel.")
									quit(1)
									return
					detail_mesh_ids[mesh.mesh.get_instance_id()] = true
				else:
					distant_mesh_ids[mesh.mesh.get_instance_id()] = true
	for i in 4:
		await physics_frame
	var space: PhysicsDirectSpaceState3D = host.world.get_world_3d().direct_space_state
	for bay in parking.get_children():
		# A shoulder-height horizontal ray must meet the vehicle's collision hull.
		var p: Vector3 = bay.global_position + Vector3.UP * .65
		var right: Vector3 = bay.global_transform.basis.z.normalized()
		var hit := space.intersect_ray(PhysicsRayQueryParameters3D.create(p + right * .67, p - right * .67))
		if hit.is_empty() or absf(p.distance_to(hit.position) - bay.scale.z * .25) > .015:
			push_error("Missing parked scooter collision: " + str(bay.name))
			quit(1)
			return
		for axle in [-.61, .61]:
			var contact: Vector3 = bay.to_global(Vector3(axle,0,0))
			var ground := space.intersect_ray(PhysicsRayQueryParameters3D.create(
					contact + Vector3.UP * .085, contact - Vector3.UP * .07))
			if ground.is_empty() or absf(ground.position.y - contact.y) > .004 or ground.normal.y < .99:
				push_error("Wheel does not touch paving in " + str(bay.name))
				quit(1)
				return
	var asset: Node3D = parking.get_parent()
	if not space.intersect_ray(PhysicsRayQueryParameters3D.create(
			asset.to_global(Vector3(31.6, 1, 1.1)), asset.to_global(Vector3(31.6, 1, -34.5)))).is_empty():
		push_error("A vehicle or building obstructs the central passage.")
		quit(1)
		return
	var directory := ProjectSettings.globalize_path("res://../renders/pe_humanities/replica").simplify_path()
	DirAccess.make_dir_recursive_absolute(directory)
	var report := FileAccess.open(directory.path_join("parking.json"),FileAccess.WRITE)
	report.store_string(JSON.stringify({"passed":true, "bays":16, "vehicle_colliders":16,
			"wheel_ground_contacts":32, "lane_clear":true, "near_mesh_resources":detail_mesh_ids.size(),
			"distant_mesh_resources":distant_mesh_ids.size(), "layout_sha256":FileAccess.get_sha256(District.COLLISION)}, "\t"))
	report.close()
	print("PARKING_CHECK_OK bays=16 collision=16 grounded_wheels=32 lane=clear unique_near_meshes=",
			detail_mesh_ids.size(), " unique_far_meshes=", distant_mesh_ids.size())
	host.free()
	quit()
