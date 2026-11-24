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
    await shot(cam,Vector3(1.2,1.68,54),Vector3(0,9,0),"avenue")
    await shot(cam,Vector3(-13.6,1.70,9.5),Vector3(-22.8,8.9,2.1),"oblique")
    await shot(cam,Vector3(-24.,1.7,8.8),Vector3(-30.,3.,2.),"columns")
    await shot(cam,Vector3(-19.,1.65,1.85),Vector3(-30.,1.65,1.85),"inside")
    await shot(cam,Vector3(1.,1.68,72.),Vector3(-6.,8.,23.),"trees")
    walker.position=Vector3(-20.,.10,1.85)
    walker.velocity=Vector3.ZERO
    walker.reset_physics_interpolation()
    for i in 8:await physics_frame
    var lateral:=InputEventKey.new()
    lateral.keycode=KEY_A
    lateral.pressed=true
    Input.parse_input_event(lateral)
    for i in 160:await physics_frame
    lateral.pressed=false
    Input.parse_input_event(lateral)
    var arcade_ok:bool=walker.position.x < -26.5 and walker.is_on_floor()
    print("ARCADE_WALK ",arcade_ok," ",walker.position)
    var passed:=arcade_ok
    for x in [-5.6,5.6]:
        walker.position=Vector3(x,.08,12.1)
        walker.velocity=Vector3.ZERO
        walker.reset_physics_interpolation()
        for i in 5:await physics_frame
        print("START ", walker.position, " rot ", walker.rotation)
        var key:=InputEventKey.new()
        key.keycode=KEY_W
        key.pressed=true
        Input.parse_input_event(key)
        for i in 350:
            await physics_frame
            if i%50==0:print("TRACE ",i," ",walker.position," ",walker.get_last_slide_collision().get_normal() if walker.get_slide_collision_count() else Vector3.ZERO)
        key.pressed=false
        Input.parse_input_event(key)
        print("STAIR_AND_LOBBY ",x," ",walker.position," floor=",walker.is_on_floor())
        passed=passed and walker.position.y>3.1 and walker.position.z< -2.0 and walker.is_on_floor()
    quit(0 if passed else 2)




