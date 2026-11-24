extends Node3D

const LIBRARY = preload("res://assets/south_library.glb")
const TREES = [preload("res://assets/tree_plane_a.glb"), preload("res://assets/tree_plane_b.glb"), preload("res://assets/tree_plane_c.glb")]
const SKY_SHADER = preload("res://samples/anime_library/daylight.gdshader")
@export var realistic := false
var forms=preload("res://samples/anime_library/tree_forms.gd").new()
var materials := {}
var rng := RandomNumberGenerator.new()

func paint(hex: String) -> StandardMaterial3D:
    if not materials.has(hex):
        var material := StandardMaterial3D.new()
        material.albedo_color = Color(hex)
        material.roughness = 0.86
        materials[hex] = material
    return materials[hex]

func block(pos: Vector3, size: Vector3, color: String) -> void:
    var mesh := BoxMesh.new()
    mesh.size = size
    var item := MeshInstance3D.new()
    item.mesh = mesh
    item.material_override = paint(color)
    item.position = pos
    add_child(item)

func tree(pos: Vector3, factor: float, variant: int) -> void:
    var species: PackedScene = forms.pick("plane") if realistic else TREES[variant]
    var item: Node3D = species.instantiate()
    item.position = pos
    item.scale *= Vector3.ONE * factor if realistic else Vector3(1.06, .89, 1.05) * factor
    item.rotation.y = rng.randf_range(-PI,PI)
    add_child(item)
    for part in item.find_children("*","MeshInstance3D",true,false):
        for i in part.mesh.get_surface_count():
            var original: Material = part.mesh.surface_get_material(i)
            if realistic and original and "Bark" in original.resource_name:
                var name_key:=original.resource_name
                if not materials.has(name_key):
                    var bark:=ShaderMaterial.new()
                    bark.shader=preload("res://samples/anime_library/bark.gdshader")
                    bark.set_shader_parameter("bark",preload("res://samples/plane_avenue/assets/plane_avenue_bark_plane_basecolor.png"))
                    bark.set_shader_parameter("relief",preload("res://samples/plane_avenue/assets/plane_avenue_bark_plane_normal.png"))
                    bark.set_shader_parameter("bark_tone",Color("b7ae88") if "Pale" in name_key else Color("736b56"))
                    materials[name_key]=bark
                part.set_surface_override_material(i,materials[name_key])
            if not realistic and original and "Leaf" in original.resource_name:
                var key := original.resource_name
                if not materials.has(key):
                    var toon := ShaderMaterial.new()
                    toon.shader = preload("res://samples/anime_library/crown.gdshader")
                    toon.set_shader_parameter("pigment", Color("89ab58") if "Light" in key else (Color("447650") if "Dark" in key else Color("678c46")))
                    materials[key] = toon
                part.set_surface_override_material(i,materials[key])

func lamp(x: float,z: float) -> void:
    var side := signf(x)
    block(Vector3(x,.14,z),Vector3(.44,.28,.44),"939ba2")
    block(Vector3(x,2.64,z),Vector3(.16,5.1,.16),"394754")
    block(Vector3(x-side*.48,5.12,z),Vector3(1.08,.13,.16),"435361")
    block(Vector3(x-side*.93,5.04,z),Vector3(.68,.16,.85),"374857")
    block(Vector3(x-side*.93,4.949,z),Vector3(.54,.03,.72),"ffedba")

func _ready():
    rng.seed=1958
    var env := Environment.new()
    env.background_mode=Environment.BG_SKY
    env.sky=Sky.new()
    var sky_material := ShaderMaterial.new()
    sky_material.shader=SKY_SHADER
    if realistic:
        var panorama:=PanoramaSkyMaterial.new()
        panorama.panorama=preload("res://samples/anime_library/fair_weather.png")
        env.sky.sky_material=panorama
    else:
        env.sky.radiance_size=Sky.RADIANCE_SIZE_1024
        env.sky.process_mode=Sky.PROCESS_MODE_QUALITY
        env.sky.sky_material=sky_material
        env.tonemap_exposure=.78
    env.tonemap_mode=Environment.TONE_MAPPER_FILMIC if realistic else Environment.TONE_MAPPER_ACES
    env.ssr_enabled=true
    env.ssao_enabled=realistic
    env.fog_enabled=true
    env.fog_sky_affect=.09
    env.fog_density=.0015 if realistic else .00042
    env.fog_light_color=Color("cfcec5") if realistic else Color("cee4ee")
    env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color=Color("e4ebff")
    env.ambient_light_energy=.35 if realistic else .34
    var world := WorldEnvironment.new()
    world.environment=env
    add_child(world)
    var sun := DirectionalLight3D.new()
    sun.rotation_degrees=Vector3(-29,-49,0) if realistic else Vector3(-43,-38,0)
    sun.light_color=Color("ffe3b5")
    sun.light_energy=1.48 if realistic else .89
    sun.shadow_enabled=true
    sun.directional_shadow_max_distance=145
    add_child(sun)
    var library := LIBRARY.instantiate()
    add_child(library)
    if realistic:
        preload("res://samples/anime_library/wing_arcade.gd").new().build(library)
    var glass := ShaderMaterial.new()
    glass.shader=preload("res://samples/anime_library/glass.gdshader")
    for part in library.find_children("*","MeshInstance3D",true,false):
        for i in part.mesh.get_surface_count():
            var original: Material = part.mesh.surface_get_material(i)
            if original is StandardMaterial3D and "TerracottaBrick" in original.resource_name:
                var brick: StandardMaterial3D = original.duplicate()
                brick.albedo_color=Color("b59892")
                if realistic:
                    var masonry:=ShaderMaterial.new()
                    masonry.shader=preload("res://samples/anime_library/masonry.gdshader")
                    masonry.set_shader_parameter("brick",preload("res://assets/textures/brick_albedo.png"))
                    masonry.set_shader_parameter("bump",preload("res://assets/textures/brick_normal.png"))
                    part.set_surface_override_material(i,masonry)
                else:
                    part.set_surface_override_material(i,brick)
            elif not realistic and original and "BlueGlazing" in original.resource_name:
                part.set_surface_override_material(i,glass)
    for part in library.find_children("*","MeshInstance3D",true,false):
        var part_name:=str(part.name)
        if part_name.begins_with("GroundStaticGlass") or "PhotoVisitGlass" in part_name or part_name.begins_with("LowerEntryGlass") or part_name.begins_with("DoorExternalFrames") or part_name.begins_with("AtriumGroundPosts"):
            part.hide()
            continue
        if part_name.begins_with("EntrySteps") or part_name.begins_with("StepNosings"):
            continue
        if part.mesh: part.create_trimesh_collision()
    var garden=preload("res://samples/anime_library/garden.gd").new()
    garden.build(self,realistic)
    preload("res://samples/anime_library/frontage.gd").new().build(self,garden,realistic)
    var autumn=preload("res://samples/anime_library/autumn.gd").new()
    autumn.build(self,garden)
    if realistic:
        autumn.sidewalks(self)
        autumn.handrails(self)
    else:
        autumn.pavers(self)
    preload("res://samples/anime_library/verge.gd").new().build(self,garden)
    if realistic:
        preload("res://samples/anime_library/streetside.gd").new().install(self,garden)
    for side in [-1,1]:
        for row in range(0 if side<0 else 2):
            for i in 9:
                var x:float=side*(9.7+row*7.8+rng.randf_range(-1.5,1.6))
                var z:float=14+i*7.85+side*1.2+row*2.6+rng.randf_range(-1.3,1.3)
                var scale_factor=rng.randf_range(.85,1.23)
                tree(Vector3(x,0,z),scale_factor*(1. if realistic else 1.14),i%3)
                garden.solid(Vector3(x,1.15,z),Vector3(.56,2.3,.56))
        for i in range(4 if realistic and side>0 else 0):
            var size_factor=rng.randf_range(.82,1.25)
            var canopy:Node3D=forms.pick("grove").instantiate()
            canopy.position=Vector3(side*(15+rng.randf_range(-2,2)),0,14+i*12)
            canopy.scale=Vector3.ONE*size_factor
            canopy.rotation.y=rng.randf()*TAU
            add_child(canopy)
        for z in [19,35,52,68]:
            lamp(side*7.4,z+side*1.2)
            garden.solid(Vector3(side*7.4,2.5,z+side*1.2),Vector3(.20,5,.20))
    var probe:=ReflectionProbe.new()
    probe.size=Vector3(108,44,125)
    probe.position=Vector3(0,4,27)
    probe.origin_offset=Vector3(0,-2.6,0)
    probe.intensity=.87 if realistic else .56
    add_child(probe)
    var walker=preload("res://samples/anime_library/walker.gd").new()
    walker.position=Vector3(1.2,.12,54)
    add_child(walker)
    rng.seed=1958
    get_window().title="图书馆南门 · 写实校园" if realistic else "图书馆南门 · 都市动漫"
    if "--capture-courtyard" in OS.get_cmdline_user_args():
        for i in 36:
            await get_tree().process_frame
        await RenderingServer.frame_post_draw
        for arg in OS.get_cmdline_user_args():
            if arg.begins_with("--capture-path="):
                print("COURTYARD_CAPTURE ",get_viewport().get_texture().get_image().save_png(arg.trim_prefix("--capture-path=")))
    if "--walk-check" in OS.get_cmdline_user_args():
        var start:Vector3=walker.position
        var key:=InputEventKey.new()
        key.keycode=KEY_W
        key.pressed=true
        Input.parse_input_event(key)
        for i in range(300 if "--walk-film" in OS.get_cmdline_user_args() else 55):
            await get_tree().physics_frame
        key.pressed=false
        Input.parse_input_event(key)
        var passed:bool=start.z-walker.position.z>1.5 and walker.is_on_floor()
        print("WALK_TEST ",passed," position=",walker.position)
        get_tree().quit(0 if passed else 1)
