extends RefCounted

const FINISH = preload("res://samples/anime_library/walkway.gdshader")
const JOINT := 0.003
const CLAY := [Color("#914e42"), Color("#955649"), Color("#8a4b40"), Color("#9c5b4c"), Color("#8c514a")]
const BORDER := [Color("#82888a"), Color("#898e8d"), Color("#7f8586")]
const GRANITE := [Color("#b4b3ab"), Color("#b8b6ae"), Color("#aeafa9"), Color("#b2b2ad")]
var rng := RandomNumberGenerator.new()
var groups := {}

# Clockwise faces. The top and four sloping shoulders share one instance mesh.
static func bevel_mesh(width:float,depth:float,top:float,bottom:float) -> ArrayMesh:
    var vertices := PackedVector3Array()
    var normals := PackedVector3Array()
    var indices := PackedInt32Array()
    var corners := [Vector2(-1,-1),Vector2(1,-1),Vector2(1,1),Vector2(-1,1)]
    var half_size := Vector2(width,depth)*0.5
    var bevel := minf(0.0028,minf(width,depth)*0.09)
    var inset := half_size - Vector2.ONE*bevel
    for corner:Vector2 in corners:
        vertices.append(Vector3(corner.x*inset.x,top,corner.y*inset.y))
        normals.append(Vector3.UP)
    indices.append_array(PackedInt32Array([0,1,2,0,2,3]))
    for i in 4:
        var a:Vector2 = corners[i]
        var b:Vector2 = corners[(i+1)%4]
        var outward := (a+b).normalized()
        var low_a := Vector3(a.x*half_size.x,bottom,a.y*half_size.y)
        var low_b := Vector3(b.x*half_size.x,bottom,b.y*half_size.y)
        var shoulder_a := Vector3(low_a.x,top-bevel*0.65,low_a.z)
        var shoulder_b := Vector3(low_b.x,top-bevel*0.65,low_b.z)
        var n := Vector3(outward.x,0,outward.y)
        var start := vertices.size()
        vertices.append_array(PackedVector3Array([low_a,low_b,shoulder_b,shoulder_a,shoulder_a,shoulder_b,vertices[(i+1)%4],vertices[i]]))
        for j in 8:
            normals.append(n if j<4 else (Vector3.UP+n*0.65).normalized())
        for face in [start,start+4]:
            indices.append_array(PackedInt32Array([face,face+1,face+2,face,face+2,face+3]))
    var arrays := []
    arrays.resize(Mesh.ARRAY_MAX)
    arrays[Mesh.ARRAY_VERTEX]=vertices
    arrays[Mesh.ARRAY_NORMAL]=normals
    arrays[Mesh.ARRAY_INDEX]=indices
    var mesh := ArrayMesh.new()
    mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
    return mesh

func stone(section:String,x:float,z:float,w:float,d:float,tones:Array):
    var size := Vector2i(roundi(w*1000),roundi(d*1000))
    if mini(size.x,size.y)<12: return
    var key := Vector3i(size.x,size.y,section.hash())
    if not groups.has(key): groups[key]=[section,[],[]]
    var group:Array = groups[key]
    group[1].append(Vector3(x+w*.5,.059+rng.randf_range(-.0006,.0006),z+d*.5))
    var tint:Color = tones[rng.randi_range(0,tones.size()-1)]
    group[2].append(tint.srgb_to_linear())

func band(section:String,x:float,z:float,w:float,d:float,along_x:bool):
    var length := w if along_x else d
    var count := maxi(1,roundi(length/.62))
    var step := length/count
    for i in count:
        if along_x: stone(section,x+step*i,z,step,d,BORDER)
        else: stone(section,x,z+step*i,w,step,BORDER)

func red_walk(section:String,left:float):
    band(section,left,8.,34.,.20,true)
    band(section,left,11.8,34.,.20,true)
    for divider in 9:
        var a := maxf(0.,divider*4.25-.125)
        var b := minf(34.,divider*4.25+.125)
        band(section,left+a,8.2,b-a,3.6,false)
    for bay in 8:
        var origin := left + bay*4.25 + .125
        # Four diagonal phases tile the grid with interlocking two-cell bricks.
        # Include the preceding row and column to cut half bricks at the border.
        for row in range(-1,36):
            for col in range(-1,40):
                var phase := posmod(col+row,4)
                if phase!=0 and phase!=2: continue
                var x0 := maxi(0,col)
                var z0 := maxi(0,row)
                var x1 := mini(40,col+(2 if phase==0 else 1))
                var z1 := mini(36,row+(1 if phase==0 else 2))
                stone(section,origin+x0*.1,8.2+z0*.1,(x1-x0)*.1,(z1-z0)*.1,CLAY)

func grey_walk(section:String,x:float,z:float,w:float,d:float):
    # Fit complete courses along the short axis, with half-length cuts at each end.
    var rows := maxi(1,roundi(d/.30))
    var depth := d/rows
    var cols := maxi(1,roundi(w/.60))
    var width := w/cols
    for row in rows:
        var offset := width*.5*(row%2)
        for col in range(-1,cols):
            var a := maxf(0.,col*width+offset)
            var b := minf(w,(col+1)*width+offset)
            stone(section,x+a,z+row*depth,b-a,depth,GRANITE)

func build(world:Node3D):
    rng.seed=94021
    red_walk("RedWest",-44.)
    red_walk("RedEast",10.)
    grey_walk("Entrance",-10.,4.5,20.,7.5)
    grey_walk("GreyWest",-44.,18.,39.,2.)
    grey_walk("GreyEast",5.,18.,39.,2.)
    var material := ShaderMaterial.new()
    material.shader=FINISH
    var meshes := {}
    for key:Vector3i in groups:
        var group:Array=groups[key]
        var size := Vector2i(key.x,key.y)
        if not meshes.has(size):
            meshes[size]=bevel_mesh(size.x*.001-JOINT,size.y*.001-JOINT,0.,-.011)
        var batch := MultiMesh.new()
        batch.transform_format=MultiMesh.TRANSFORM_3D
        batch.use_colors=true
        batch.mesh=meshes[size]
        batch.instance_count=group[1].size()
        for i in batch.instance_count:
            batch.set_instance_transform(i,Transform3D(Basis.IDENTITY,group[1][i]))
            batch.set_instance_color(i,group[2][i])
        var node := MultiMeshInstance3D.new()
        node.name=group[0]+"Pavers"
        node.multimesh=batch
        node.material_override=material
        node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
        world.add_child(node,true)
