extends SceneTree

func _initialize():
    run.call_deferred()

func run():
    var args:=OS.get_cmdline_user_args()
    if args.size()>0:
        if not ProjectSettings.load_resource_pack(args[0],true):
            quit(1)
            return
    var world=load("res://samples/anime_library/realistic.tscn").instantiate()
    root.add_child(world)
    root.mode=Window.MODE_WINDOWED
    root.size=Vector2i(1920,1080)
    root.content_scale_size=Vector2i(1920,1080)
    Engine.max_fps=0
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    var cam:=Camera3D.new()
    world.add_child(cam)
    cam.current=true
    var vp:=root.get_viewport_rid()
    RenderingServer.viewport_set_measure_render_time(vp,true)
    print("INFO ",RenderingServer.get_video_adapter_name()," ",root.get_visible_rect().size," ",RenderingServer.get_current_rendering_method()," scaling ",root.scaling_3d_scale)
    for route in 2:
        var samples:Array[float]=[]
        var gpu:Array[float]=[]
        var calls:Array[float]=[]
        var tris:Array[float]=[]
        var mem:Array[float]=[]
        var last:=Time.get_ticks_usec()
        for i in 370:
            var t:=clampf(float(i-70)/299.,0,1)
            cam.position=Vector3(1.2,1.7,54.-t*37.) if route==0 else Vector3(5.9,1.7,55.-t*33.)
            cam.look_at(cam.position+(Vector3(-.025,.12,-1.) if route==0 else Vector3(.60,.02,-1.)))
            await RenderingServer.frame_post_draw
            var now:=Time.get_ticks_usec()
            if i>=70:
                samples.append((now-last)/1000.)
                gpu.append(RenderingServer.viewport_get_measured_render_time_gpu(vp))
                calls.append(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
                tris.append(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME))
                mem.append(Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)/1048576.)
            last=now
        samples.sort()
        gpu.sort()
        calls.sort()
        tris.sort()
        mem.sort()
        print("RESULT route=",route," median_ms=",samples[150]," p95_ms=",samples[284]," gpu_ms=",gpu[150]," draws=",calls[150]," primitives=",tris[150]," mem_MiB=",mem[299])
    quit()
