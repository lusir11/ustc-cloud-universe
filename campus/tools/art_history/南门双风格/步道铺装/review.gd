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
    await shot(cam,Vector3(17.6,1.68,11.1),Vector3(20.6,0,10.35),"red_walk")
    await shot(cam,Vector3(18.0,1.35,11.5),Vector3(18.55,.05,10.9),"bond")
    await shot(cam,Vector3(6.32,1.68,47.1),Vector3(6.35,.06,44.4),"avenue_walk")
    await shot(cam,Vector3(9.45,1.68,13.1),Vector3(10.2,.05,10.5),"junction")
    world.queue_free()
    for i in 8: await process_frame
    quit()
