extends Node3D

var leaves:Array[AnimatableBody3D]=[]

func pane()->StandardMaterial3D:
    var mat:=StandardMaterial3D.new()
    mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
    mat.albedo_color=Color(.39,.57,.65,.54)
    mat.metallic=.67
    mat.metallic_specular=.85
    mat.roughness=.08
    return mat

func box(parent:Node3D,center:Vector3,size:Vector3,mat:Material):
    var mesh:=BoxMesh.new()
    mesh.size=size
    var part:=MeshInstance3D.new()
    part.mesh=mesh
    part.material_override=mat
    part.position=center
    parent.add_child(part)

func install(world):
    var glass:=pane()
    for side in [-1,1]:
        var door:=AnimatableBody3D.new()
        door.position=Vector3(side*1.20,4.305,.225)
        add_child(door)
        leaves.append(door)
        var size:=Vector3(2.23,2.24,.033)
        box(door,Vector3.ZERO,size,glass)
        for y in [-1.10,1.10]:
            box(door,Vector3(0,y,0),Vector3(2.24,.044,.046),world.paint("525d5d"))
        box(door,Vector3(-side*1.10,0,0),Vector3(.034,2.23,.045),world.paint("515958"))
        box(door,Vector3(0,-.21,.023),Vector3(2.18,.045,.007),world.paint("557f88"))
        var collider:=CollisionShape3D.new()
        var shape:=BoxShape3D.new()
        shape.size=size
        collider.shape=shape
        door.add_child(collider)
    # A local reflection capture sees the avenue from the plane of the entrance.
    var probe:=ReflectionProbe.new()
    probe.size=Vector3(25,24,20)
    probe.position=Vector3(0,9,.7)
    probe.origin_offset=Vector3(0,-2,2)
    probe.box_projection=false
    probe.intensity=1.0
    add_child(probe)

func _physics_process(dt):
    var visitor:=get_tree().get_first_node_in_group("library_visitor") as Node3D
    if not visitor:return
    var at:=to_local(visitor.global_position)
    var near:=absf(at.x)<3.45 and absf(at.z-.225)<3.6 and absf(at.y-3.18)<1.
    for i in leaves.size():
        var side:float=-1 if i==0 else 1
        leaves[i].position.x=move_toward(leaves[i].position.x,side*(3.49 if near else 1.20),dt*3.7)

