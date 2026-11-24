extends SceneTree

func _initialize():
    run.call_deferred()

func shot(camera:Camera3D,from:Vector3,target:Vector3,file:String):
    camera.global_position=from
    camera.look_at(target)
    camera.reset_physics_interpolation()
    for i in 6: await process_frame
    await RenderingServer.frame_post_draw
    var dir:=OS.get_cmdline_user_args()[0]
    print(file," ",root.get_texture().get_image().save_png(dir.path_join(file+".png")))

func run():
    var world=load("res://samples/anime_library/realistic.tscn").instantiate()
    root.add_child(world)
    for i in 8:await physics_frame
    var walker:CharacterBody3D=world.find_children("*","CharacterBody3D",true,false)[0]
    var cam:=Camera3D.new()
    world.add_child(cam)
    cam.current=true
    await shot(cam,Vector3(16.9,1.6,11.2),Vector3(20.1,.6,6.64),"parking")
    await shot(cam,Vector3(-7.55,.43,40.30),Vector3(-7.92,.235,40.94),"black")
    await shot(cam,Vector3(7.60,.44,44.26),Vector3(7.92,.21,44.96),"calico")
    walker.position=Vector3(1.2,3.21,4.)
    walker.reset_physics_interpolation()
    for i in 8:await physics_frame
    var key:=InputEventKey.new()
    key.keycode=KEY_W
    key.pressed=true
    Input.parse_input_event(key)
    Input.flush_buffered_events()
    for i in 220:await physics_frame
    key.pressed=false
    Input.parse_input_event(key)
    Input.flush_buffered_events()
    var ok:bool=walker.position.z< -4. and walker.is_on_floor()
    for i in 70:await physics_frame
    var doors=world.find_children("*","AnimatableBody3D",true,false)
    print("ENTRY ",ok," ",walker.position," closed leaf positions ",doors[0].position.x," ",doors[1].position.x)
    quit(0 if ok else 2)

