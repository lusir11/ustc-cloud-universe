extends SceneTree

func _initialize():
    capture.call_deferred()

func capture():
    var game=load("res://scenes/campus_game.tscn").instantiate()
    root.add_child(game)
    for i in 5: await process_frame
    if not game.game_ready:
        quit(2)
        return
    game.process_mode=Node.PROCESS_MODE_DISABLED
    var survey:=SubViewport.new()
    survey.size=Vector2i(3360,4400)
    survey.world_3d=root.world_3d
    survey.use_occlusion_culling=false
    survey.render_target_update_mode=SubViewport.UPDATE_DISABLED
    root.add_child(survey)
    for node in game.find_children("*","GeometryInstance3D",true,false):
        if node.visibility_range_begin>0.0 or node is Label3D:
            node.hide()
        else:
            node.visibility_range_end=0.
    for light in game.find_children("*","DirectionalLight3D",true,false):
        light.shadow_enabled=false
    var site=JSON.parse_string(FileAccess.get_file_as_string("res://assets/site.json"))
    var a:float=site.south_rotation_radians
    var east:=Vector3(cos(a),0,sin(a))
    var south:=Vector3(-sin(a),0,cos(a))
    var cam:=Camera3D.new()
    survey.add_child(cam)
    cam.cull_mask=game.player.camera.cull_mask
    cam.transform=Transform3D(Basis(east,-south,Vector3.UP),east*20.+south*410.+Vector3.UP*240.)
    cam.set_orthogonal(1100.,.1,1400.)
    cam.keep_aspect=Camera3D.KEEP_HEIGHT
    cam.current=true
    var env:Environment=root.world_3d.environment.duplicate()
    env.fog_enabled=false
    env.volumetric_fog_enabled=false
    env.ssao_enabled=false
    env.ssil_enabled=false
    env.ssr_enabled=false
    env.glow_enabled=false
    env.adjustment_enabled=false
    if env.sky:
        env.ambient_light_source=Environment.AMBIENT_SOURCE_SKY
        env.reflected_light_source=Environment.REFLECTION_SOURCE_SKY
    env.background_mode=Environment.BG_COLOR
    env.background_color=Color("#3f4745")
    cam.environment=env
    var origin_px:=cam.unproject_position(Vector3.ZERO)
    var east_px:=cam.unproject_position(east*100.)
    var north_px:=cam.unproject_position(-south*100.)
    print("MAP origin=",origin_px," east100=",east_px," north100=",north_px)
    if origin_px.distance_to(Vector2(1600,560))>.2 or east_px.distance_to(origin_px+Vector2(400,0))>.2 or north_px.distance_to(origin_px-Vector2(0,400))>.2:
        quit(3)
        return
    survey.render_target_update_mode=SubViewport.UPDATE_ALWAYS
    for i in 4: await process_frame
    await RenderingServer.frame_post_draw
    var im:=survey.get_texture().get_image()
    var out:=OS.get_cmdline_user_args()[0]
    var err:=im.save_png(out.path_join("东区模型正射底图.png"))
    print("MAP saved ",im.get_size()," ",err)
    quit(0 if err==OK else 4)
