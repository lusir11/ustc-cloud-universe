extends SceneTree

func _initialize():
    run.call_deferred()

func shot(cam:Camera3D,eye:Vector3,at:Vector3,file:String):
    cam.global_position=eye
    cam.look_at(at)
    cam.reset_physics_interpolation()
    for i in 5: await process_frame
    await RenderingServer.frame_post_draw
    var out:=OS.get_cmdline_user_args()[0].path_join(file+".png")
    print(file," capture ",root.get_texture().get_image().save_png(out))

func run():
    var world=load("res://samples/anime_library/realistic.tscn").instantiate()
    root.add_child(world)
    for i in 8: await physics_frame
    var cam:=Camera3D.new()
    world.add_child(cam)
    cam.current=true
    await shot(cam,Vector3(-17.65,1.7,10.15),Vector3(-20.1,.55,6.65),"bikes")
    await shot(cam,Vector3(4.4,1.60,23.4),Vector3(7.26,.64,23.05),"bench")
    var west_bikes:Array[AABB]=[]
    var seats:=0
    var ok:=true
    for obj in world.get_children():
        if obj.scene_file_path.ends_with("/bicycle.glb") and obj.position.x<0:
            var bounds:=mesh_bounds(obj)
            ok=ok and bounds.position.z>5.4 and bounds.end.z<7.88 and bounds.position.x > -22.37 and bounds.end.x < -17.67
            for other in west_bikes:
                ok=ok and not other.intersects(bounds)
            west_bikes.append(bounds)
        if obj.scene_file_path.ends_with("/bench.glb") and obj.position.z<30:
            var bounds:=mesh_bounds(obj)
            var side:=signf(obj.position.x)
            var lamp_z:=23.+side*1.2
            var clearance:=maxf(bounds.position.z-(lamp_z+.22),(lamp_z-.22)-bounds.end.z)
            var fence_gap:=25.-.044-bounds.end.z
            var has_body:=false
            for body in world.get_children():
                if body is StaticBody3D and body.position.is_equal_approx(obj.position+Vector3.UP*.4):
                    has_body=true
                    break
            ok=ok and clearance>.4 and fence_gap>.3 and has_body
            print("Bench ",side," lamp gap ",clearance," rail gap ",fence_gap," collider ",has_body)
            seats+=1
    ok=ok and west_bikes.size()==4 and seats==2
    print("Placement check ",ok," bikes ",west_bikes.size()," benches ",seats)
    world.queue_free()
    for i in 8: await process_frame
    quit(0 if ok else 2)

func mesh_bounds(obj:Node3D)->AABB:
    var box:=AABB()
    var first:=true
    for part in obj.find_children("*","MeshInstance3D",true,false):
        var b:AABB=part.global_transform*part.get_aabb()
        box=b if first else box.merge(b)
        first=false
    return box
