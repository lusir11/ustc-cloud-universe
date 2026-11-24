extends SceneTree

func _initialize():
    run.call_deferred()

func shot(cam:Camera3D,eye:Vector3,at:Vector3,file:String):
    cam.global_position=eye
    cam.look_at(at)
    cam.reset_physics_interpolation()
    for i in 5: await process_frame
    await RenderingServer.frame_post_draw
    var out:=OS.get_cmdline_user_args()[0].path_join(OS.get_cmdline_user_args()[1]+"_"+file+".png")
    print(file," capture ",root.get_texture().get_image().save_png(out))

func run():
    var world=load("res://samples/anime_library/realistic.tscn").instantiate()
    root.add_child(world)
    for i in 8: await physics_frame
    var cam:=Camera3D.new()
    world.add_child(cam)
    cam.current=true
    await shot(cam,Vector3(2.1,1.68,55.8),Vector3(1.8,.85,40.0),"avenue")
    await shot(cam,Vector3(3.28,1.65,52.5),Vector3(4.66,.03,50.35),"detail")
    await shot(cam,Vector3(4.0,1.68,20.1),Vector3(-4.0,.6,14.1),"junction")
    world.queue_free()
    for i in 8: await process_frame
    quit()
