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
    await shot(cam,Vector3(5.,1.68,39.),Vector3(7.38,2.8,34.5),"sign")
    await shot(cam,Vector3(5.1,1.4,28.),Vector3(4.45,.6,23.),"cones")
    await shot(cam,Vector3(-7.65,.78,58.35),Vector3(-8.60,.35,57.1),"plants")
    await shot(cam,Vector3(5.75,2.85,38.7),Vector3(6.84,3.94,36.35),"camera")
    world.hide()
    var studio:=Node3D.new()
    root.add_child(studio)
    var camera:=Camera3D.new()
    studio.add_child(camera)
    camera.projection=Camera3D.PROJECTION_ORTHOGONAL
    camera.size=71.
    camera.keep_aspect=Camera3D.KEEP_WIDTH
    camera.position=Vector3(0,6,40)
    camera.look_at(Vector3(0,6,0))
    camera.current=true
    var sun:=DirectionalLight3D.new()
    studio.add_child(sun)
    sun.rotation_degrees=Vector3(-44,-32,0)
    sun.light_energy=1.4
    var back:=WorldEnvironment.new()
    var env:=Environment.new()
    env.background_mode=Environment.BG_COLOR
    env.background_color=Color("aebac2")
    env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color=Color("f0eee8")
    env.ambient_light_energy=.75
    camera.environment=env
    var output:=OS.get_cmdline_user_args()[0]
    for family in ["cedar","plane","grove"]:
        for bank in 2:
            var row:=Node3D.new()
            studio.add_child(row)
            for i in 5:
                var tree:Node3D=load("res://samples/anime_library/forms/%s_%d.glb"%[family,bank*5+i]).instantiate()
                row.add_child(tree)
                tree.position.x=(i-2)*14.
            for i in 8:await process_frame
            await RenderingServer.frame_post_draw
            root.get_texture().get_image().save_png(output.path_join("%s_%d.png"%[family,bank]))
            row.queue_free()
            await process_frame
    quit()
