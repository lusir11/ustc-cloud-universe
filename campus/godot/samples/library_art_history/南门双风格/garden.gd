extends RefCounted
const GROUND = preload("res://samples/anime_library/ground.gdshader")
const ASPHALT="res://samples/plane_avenue/assets/plane_avenue_asphalt_"
var world:Node3D
var rng:=RandomNumberGenerator.new()
var real:bool
var mats:Dictionary={}
var batches:Dictionary={}
var meshes:Dictionary={}

func slab(center:Vector3,size:Vector3,material:Material):
    var item:=MeshInstance3D.new()
    var cube:=BoxMesh.new()
    cube.size=size
    item.mesh=cube
    item.material_override=material
    item.position=center
    world.add_child(item)

func solid(center:Vector3,size:Vector3):
    var body:=StaticBody3D.new()
    var collider:=CollisionShape3D.new()
    var shape:=BoxShape3D.new()
    shape.size=size
    collider.shape=shape
    body.position=center
    body.add_child(collider)
    world.add_child(body)

func surf(color:String,base:String,normal:String,meters:float,road:bool=false)->ShaderMaterial:
    var m:=ShaderMaterial.new()
    m.shader=GROUND
    m.set_shader_parameter("tint",Color(color))
    m.set_shader_parameter("base",load(base))
    m.set_shader_parameter("normal_tex",load(normal))
    m.set_shader_parameter("metres",meters)
    m.set_shader_parameter("realistic",real)
    m.set_shader_parameter("road",road)
    return m

func asset(name:String,pos:Vector3,sc:Vector3,yaw:float):
    var obj:Node3D=load("res://assets/"+name+".glb").instantiate()
    obj.position=pos
    obj.rotation.y=yaw
    obj.scale=sc
    world.add_child(obj)

func scatter(kind:String,pos:Vector3,sc:Vector3,angle:float):
    var basis:=Basis(Vector3.UP,angle).scaled_local(sc)
    batches[kind].append(Transform3D(basis,pos))

func small_mesh(points:Array,indices:Array)->ArrayMesh:
    var st:=SurfaceTool.new()
    st.begin(Mesh.PRIMITIVE_TRIANGLES)
    for i in indices:
        st.add_vertex(points[i])
    st.generate_normals()
    return st.commit()

func build(parent:Node3D,realistic:bool):
    world=parent
    real=realistic
    rng.seed=20261118
    var tx="res://assets/textures/"
    slab(Vector3(0,-.12,16),Vector3(174,.22,166),surf("809953" if real else "91b661",tx+"grass_albedo.png",tx+"grass_normal.png",2.3))
    slab(Vector3(0,.004,44),Vector3(10,.07,68),surf("666669" if real else "86848a",ASPHALT+"basecolor.png",ASPHALT+"normal.png",2.1,true))
    var paving=surf("cbbba5",tx+"paving_albedo.png",tx+"paving_normal.png",3.2)
    slab(Vector3(0,.021,10),Vector3(82,.10,8),paving)
    solid(Vector3(0,-.17,17),Vector3(172,.34,166))
    for side in [-1,1]:
        slab(Vector3(side*6.25,.03,46),Vector3(2.38,.12,64),paving)
        for j in 53:
            var col:String=["beb8a6","b5b19f","c1bda9"][rng.randi_range(0,2)]
            world.block(Vector3(side*5.05,.066,14.6+j*1.20),Vector3(.19,.2,1.178),col)
        for z in [24,43,62]:
            world.block(Vector3(side*4.83,.045,z),Vector3(.24,.014,.62),"404645")
            for slit in 6:
                world.block(Vector3(side*4.83,.055,z-.24+.09*slit),Vector3(.17,.009,.034),"22292a")
        for z in [24,48]:
            var p:=Vector3(side*7.5,0,z)
            asset("bench",p,Vector3.ONE,side*PI/2)
            solid(p+Vector3.UP*.40,Vector3(.62,.8,1.9))
        for i in 4:
            asset("bicycle",Vector3(side*(8.6+i*.69),0,17+side*1.3),Vector3.ONE,.92+side*.24)
        for i in 35:
            var z:=rng.randf_range(19,76)
            var p:=Vector3(side*rng.randf_range(8.8,13.8),0,z)
            var s:=rng.randf_range(.52,1.20)
            asset("sakura_shrub_"+str(i%3),p,Vector3(s,s*.78,s),rng.randf()*TAU)
        for i in 8:
            var s:=rng.randf_range(.48,.81)
            asset("study_flower_mound_0",Vector3(side*rng.randf_range(7.95,9.15),0,22+i*6),Vector3.ONE*s,rng.randf()*TAU)
    # Bound the exterior walk to the finished garden.
    for x in [-33,33]:
        solid(Vector3(x,2,41),Vector3(.3,4,78))
    solid(Vector3(0,2,78),Vector3(66,4,.3))
    solid(Vector3(0,2,-30),Vector3(174,4,.3))
    var leaf:=small_mesh([Vector3(0,.04,0),Vector3(-.5,0,.12),Vector3(-.23,.01,-.17),Vector3(-.29,.01,-.40),Vector3(-.08,.01,-.28),Vector3(0,0,-.6),Vector3(.12,0,-.27),Vector3(.37,.02,-.44),Vector3(.25,.02,-.1),Vector3(.52,.01,.1),Vector3(.04,.01,.29)],[0,2,1,0,3,2,0,4,3,0,5,4,0,6,5,0,7,6,0,8,7,0,9,8,0,10,9,0,1,10])
    var blades:=small_mesh([Vector3(-.10,0,0),Vector3(.07,0,0),Vector3(.15,.51,.03),Vector3(0,0,-.1),Vector3(0,0,.09),Vector3(-.08,.42,.15),Vector3(-.19,0,.09),Vector3(-.05,0,.15),Vector3(-.22,.34,.23)],[0,1,2,3,4,5,6,7,8])
    var colors=["c19042","975b2d","b89f59","63804b","94a855"]
    for i in 5:
        var key=str(i)
        meshes[key]=leaf if i<3 else blades
        var m:StandardMaterial3D=world.paint(colors[i]).duplicate()
        m.cull_mode=BaseMaterial3D.CULL_DISABLED
        mats[key]=m
        batches[key]=[]
    for i in 12000:
        var side=-1 if i%2==0 else 1
        var z:=rng.randf_range(15,78)
        var x:float=side*(7.55+pow(rng.randf(),1.5)*17.)
        var s:=rng.randf_range(.26,.72)
        scatter(str(rng.randi_range(3,4)),Vector3(x,.0,z),Vector3.ONE*s,rng.randf()*TAU)
    for i in 1100:
        var x:=rng.randf_range(-18,18)
        var z:=rng.randf_range(16,77)
        if absf(x)<3 and rng.randf()<.85:continue
        var h:=.045 if absf(x)<5 else (.096 if absf(x)<7.48 else .003)
        scatter(str(i%3),Vector3(x,h,z),Vector3.ONE*rng.randf_range(.12,.29),rng.randf()*TAU)
    for key in batches:
        var batch:=MultiMesh.new()
        batch.transform_format=MultiMesh.TRANSFORM_3D
        batch.mesh=meshes[key]
        batch.instance_count=batches[key].size()
        for i in batch.instance_count:
            batch.set_instance_transform(i,batches[key][i])
        var node:=MultiMeshInstance3D.new()
        node.multimesh=batch
        node.material_override=mats[key]
        node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
        world.add_child(node)
