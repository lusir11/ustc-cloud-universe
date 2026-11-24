extends Node3D

const LIBRARY = preload("res://assets/south_library.glb")
const TREES = [preload("res://assets/tree_plane_a.glb"), preload("res://assets/tree_plane_b.glb"), preload("res://assets/tree_plane_c.glb")]
const FOLIAGE = preload("res://samples/anime_library/foliage.gdshader")
const SKY_SHADER = preload("res://samples/anime_library/daylight.gdshader")
var camera := Camera3D.new()
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
    var item: Node3D = TREES[variant].instantiate()
    item.position = pos
    item.scale *= factor
    item.rotation.y = rng.randf_range(-PI,PI)
    add_child(item)
    for part in item.find_children("*","MeshInstance3D",true,false):
        for i in part.mesh.get_surface_count():
            var original: Material = part.mesh.surface_get_material(i)
            if original and "Leaf" in original.resource_name:
                var key := original.resource_name
                if not materials.has(key):
                    var toon := ShaderMaterial.new()
                    toon.shader = FOLIAGE
                    toon.set_shader_parameter("pigment", Color("9cbc58") if "Light" in key else (Color("447650") if "Dark" in key else Color("79a44b")))
                    materials[key] = toon
                part.set_surface_override_material(i,materials[key])

func lamp(x: float,z: float) -> void:
    var side := signf(x)
    block(Vector3(x,.14,z),Vector3(.44,.28,.44),"939ba2")
    block(Vector3(x,2.64,z),Vector3(.16,5.1,.16),"394754")
    block(Vector3(x-side*.48,5.12,z),Vector3(1.08,.13,.16),"435361")
    block(Vector3(x-side*.93,5.04,z),Vector3(.68,.16,.85),"374857")
    block(Vector3(x-side*.93,4.949,z),Vector3(.54,.03,.72),"ffedba")

func garden_strip(x: float) -> void:
    # Flower heads share one draw batch for each palette colour.
    for tone in ["9e9bd2","d6c6ed","f4ead2","668c49"]:
        var batch := MultiMesh.new()
        batch.transform_format = MultiMesh.TRANSFORM_3D
        var bud := SphereMesh.new()
        bud.radial_segments=6
        bud.rings=3
        batch.mesh=bud
        batch.instance_count=260
        for i in batch.instance_count:
            var z := rng.randf_range(17,66)
            var spread := sin(z*.62)*.38
            var p := Vector3(x+spread+rng.randf_range(-.65,.65),rng.randf_range(.10,.28),z)
            var s := rng.randf_range(.09,.21)
            batch.set_instance_transform(i,Transform3D(Basis().scaled(Vector3(s*1.6,s,s*1.6)),p))
        var item := MultiMeshInstance3D.new()
        item.multimesh=batch
        item.material_override=paint(tone)
        add_child(item)

func _ready():
    rng.seed=1958
    var env := Environment.new()
    env.background_mode=Environment.BG_SKY
    env.sky=Sky.new()
    var sky_material := ShaderMaterial.new()
    sky_material.shader=SKY_SHADER
    env.sky.sky_material=sky_material
    env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color=Color("e4ebff")
    env.ambient_light_energy=.52
    var world := WorldEnvironment.new()
    world.environment=env
    add_child(world)
    var sun := DirectionalLight3D.new()
    sun.rotation_degrees=Vector3(-39,-34,0)
    sun.light_color=Color("ffe3b5")
    sun.light_energy=1.12
    sun.shadow_enabled=true
    sun.directional_shadow_max_distance=145
    add_child(sun)
    var library := LIBRARY.instantiate()
    add_child(library)
    var glass := ShaderMaterial.new()
    glass.shader=preload("res://samples/anime_library/glass.gdshader")
    for part in library.find_children("*","MeshInstance3D",true,false):
        for i in part.mesh.get_surface_count():
            var original: Material = part.mesh.surface_get_material(i)
            if original is StandardMaterial3D and "TerracottaBrick" in original.resource_name:
                var brick: StandardMaterial3D = original.duplicate()
                brick.albedo_color=Color("b59892")
                part.set_surface_override_material(i,brick)
            elif original and "BlueGlazing" in original.resource_name:
                part.set_surface_override_material(i,glass)
    block(Vector3(0,-.18,19),Vector3(200,.32,175),"739554")
    block(Vector3(0,-.025,9),Vector3(93,.09,14),"c2b7a4")
    for row in 26:
        for col in 6:
            var shade: String = ["d2c4af","d8cab7","cfc2ad","d6c8b4"][rng.randi_range(0,3)]
            block(Vector3((col-2.5)*1.75,.004,17+row*2.4),Vector3(1.739,.08,2.388),shade)
    for side in [-1,1]:
        block(Vector3(side*5.36,.055,47),Vector3(.22,.16,62),"e8deca")
        garden_strip(side*6.18)
        for i in 5:
            tree(Vector3(side*(9.6+rng.randf_range(0,2)),0,16+i*13.0+side*1.8),rng.randf_range(.78,1.05),i%3)
        for z in [22,38,55]:
            lamp(side*5.9,z+side*1.2)
    camera.fov=57
    camera.position=Vector3(0,2.4,56)
    add_child(camera)
    camera.look_at(Vector3(0,12,0))
    camera.current=true
    if "--capture-courtyard" in OS.get_cmdline_user_args():
        for frame in 20:
            await get_tree().process_frame
        await RenderingServer.frame_post_draw
        var output=ProjectSettings.globalize_path("res://../../../图书馆动漫样景.png")
        for arg in OS.get_cmdline_user_args():
            if arg.begins_with("--capture-path="):
                output=arg.trim_prefix("--capture-path=")
        print("COURTYARD_CAPTURE ",get_viewport().get_texture().get_image().save_png(output))

func _unhandled_input(event):
    if event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
        camera.rotation.y-=event.relative.x*.003
        camera.rotation.x=clampf(camera.rotation.x-event.relative.y*.003,-1.3,1.3)

func _process(delta):
    var input := Vector3(float(Input.is_key_pressed(KEY_D))-float(Input.is_key_pressed(KEY_A)),0,float(Input.is_key_pressed(KEY_S))-float(Input.is_key_pressed(KEY_W)))
    var walk := camera.global_basis*input
    walk.y=0
    camera.position+=walk.normalized()*delta*5.5
    camera.position.x=clampf(camera.position.x,-15,15)
    camera.position.z=clampf(camera.position.z,15,72)
