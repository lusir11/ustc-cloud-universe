extends RefCounted

const PRINTS = preload("res://samples/anime_library/club_prints.jpg")
var rng:=RandomNumberGenerator.new()

func build(world, garden):
    rng.seed=43828
    entrance(world,garden)
    creeper(world)
    for side in [-1,1]:
        bins(world,garden,side*7.02,36.0+side*3.)
        var pos:=Vector3(side*7.90,.015,43.+side*2.)
        garden.asset("campus_cat",pos,Vector3.ONE*.84,side*.8)

func entrance(world,garden):
    # Convex ramps follow the two original stair flights and meet the landing at 3.18 m.
    for side in [-1,1]:
        var points:=PackedVector3Array()
        for x in [side*5.91-3.4,side*5.91+3.4]:
            points.append(Vector3(x,-.10,11.12))
            points.append(Vector3(x,.035,11.12))
            points.append(Vector3(x,-.10,4.46))
            points.append(Vector3(x,3.18,4.46))
        var ramp:=ConvexPolygonShape3D.new()
        ramp.points=points
        var collider:=CollisionShape3D.new()
        collider.shape=ramp
        var body:=StaticBody3D.new()
        body.add_child(collider)
        world.add_child(body)
    for spec in [
        [Vector3(0,3.07,-3.95),Vector3(14.2,.22,8.)],
        [Vector3(0,5.40,-7.89),Vector3(14.3,4.65,.22)],
        [Vector3(-7.06,5.4,-3.98),Vector3(.22,4.65,8.)],
        [Vector3(7.06,5.4,-3.98),Vector3(.22,4.65,8.)]]:
        world.block(spec[0],spec[1],"c5af92")
        garden.solid(spec[0],spec[1])
    world.block(Vector3(0,7.69,-3.95),Vector3(14.2,.15,8.),"e0d1b7")
    for col in 3:
        var x:float=(col-1)*2.55
        world.block(Vector3(x,5.24,-7.72),Vector3(2.02,2.91,.09),"5b493b")
        var sheet:=QuadMesh.new()
        sheet.size=Vector2(1.93,2.81)
        var mat:=StandardMaterial3D.new()
        mat.albedo_texture=PRINTS
        mat.uv1_scale=Vector3(1./3.,1.,1.)
        mat.uv1_offset=Vector3(col/3.,0,0)
        mat.emission_enabled=true
        mat.emission_texture=PRINTS
        mat.emission_energy_multiplier=.23
        var print_node:=MeshInstance3D.new()
        print_node.mesh=sheet
        print_node.material_override=mat
        print_node.position=Vector3(x,5.24,-7.65)
        world.add_child(print_node)
        var light:=OmniLight3D.new()
        light.position=Vector3(x,6.35,-5.25)
        light.omni_range=5.5
        light.light_color=Color("fff0d7")
        light.light_energy=1.2
        world.add_child(light)

func bins(world,garden,x:float,z:float):
    var colors=["2785a4","6b9553","d76050","e0a440"]
    for k in 4:
        var at:=Vector3(x,0,z+k*.55)
        world.block(at+Vector3.UP*.50,Vector3(.46,.82,.49),colors[k])
        world.block(at+Vector3.UP*.94,Vector3(.49,.085,.52),"46535a")
        world.block(at+Vector3(0,.985,0),Vector3(.26,.015,.28),"233336")
        world.block(at+Vector3(.233*signf(-x),.58,0),Vector3(.014,.16,.17),"fff0ca")
        var label:=Label3D.new()
        label.text=["RECYCLE","ORGANIC","HAZARD","OTHER"][k]
        label.font_size=54
        label.pixel_size=.00079
        label.outline_size=0
        label.rotation.y=-signf(x)*PI/2
        label.position=at+Vector3(-signf(x)*.238,.44,0)
        world.add_child(label)
        garden.solid(at+Vector3.UP*.5,Vector3(.48,1.,.50))

func leaf_mesh()->ArrayMesh:
    var mesh:=SurfaceTool.new()
    mesh.begin(Mesh.PRIMITIVE_TRIANGLES)
    var outline=[Vector2(0,.50),Vector2(-.45,.28),Vector2(-.39,.04),Vector2(-.59,-.20),Vector2(-.23,-.14),Vector2(0,-.64),Vector2(.21,-.14),Vector2(.57,-.20),Vector2(.38,.045),Vector2(.44,.26)]
    for i in outline.size():
        for j in [-1,i,(i+1)%outline.size()]:
            if j==-1:
                mesh.add_vertex(Vector3(0,0,.115))
            else:
                var p:Vector2=outline[j]
                mesh.add_vertex(Vector3(p.x,p.y,0))
    mesh.generate_normals()
    return mesh.commit()

func creeper(world):
    var poses:Array[Transform3D]=[]
    var colors:Array[Color]=[]
    var stems:=SurfaceTool.new()
    stems.begin(Mesh.PRIMITIVE_TRIANGLES)
    for side in [-1,1]:
        # Gray ground-floor cladding on the wings and the two stone portal piers.
        for pier in [false,true]:
            var face_z:=4.53 if pier else .35
            var mid:float=side*(9.31 if pier else 26.1)
            var span:=.40 if pier else 7.2
            for branch in range(8 if pier else 54):
                var bias:=rng.randf_range(-1,1)
                var origin:=mid+bias*span*.78
                var height:float=(11.4 if pier else 3.05)*rng.randf_range(.45,1.)*(1.-absf(bias)*.21)
                var last:=Vector3(origin,.12,face_z)
                var phase:=rng.randf()*TAU
                var shots:=ceili(height/.085)
                for k in shots:
                    var t:float=(k+1.)/shots
                    var xx:float=origin+sin(t*6.+phase)*(.09 if pier else .40)*t+bias*t*span*.16
                    var at:=Vector3(xx,.12+t*height,face_z+.011)
                    var half_width:=Vector3(.011*(1.-t*.7),0,0)
                    for v in [last-half_width,last+half_width,at+half_width,last-half_width,at+half_width,at-half_width]:
                        stems.add_vertex(v)
                    last=at
                    for l in 3:
                        var spread:=rng.randf_range(-.17,.17)*(1.-t*.65)
                        var loc:=at+Vector3(spread,rng.randf_range(-.09,.09),rng.randf_range(.012,.054))
                        var sz:=rng.randf_range(.10,.20)*(1.-t*.31)
                        poses.append(Transform3D(Basis(Vector3.BACK,rng.randf_range(-.85,.85)).scaled_local(Vector3.ONE*sz),loc))
                        var autumn:=clampf(.36+t*.41+sin(origin*1.7+t*3.)*.29+rng.randf_range(-.12,.12),0,1)
                        var palette=[Color("366744"),Color("64823e"),Color("c59b3e"),Color("c95b3e"),Color("9b3246")]
                        var tone:=autumn*3.999
                        colors.append(palette[int(tone)].lerp(palette[int(tone)+1],fmod(tone,1.)).srgb_to_linear())
    stems.generate_normals()
    var vine:=MeshInstance3D.new()
    vine.mesh=stems.commit()
    var twig:StandardMaterial3D=world.paint("735645").duplicate()
    twig.cull_mode=BaseMaterial3D.CULL_DISABLED
    vine.material_override=twig
    world.add_child(vine)
    var leaves:=MultiMesh.new()
    leaves.transform_format=MultiMesh.TRANSFORM_3D
    leaves.use_colors=true
    leaves.mesh=leaf_mesh()
    leaves.instance_count=poses.size()
    for i in poses.size():
        leaves.set_instance_transform(i,poses[i])
        leaves.set_instance_color(i,colors[i])
    var node:=MultiMeshInstance3D.new()
    node.multimesh=leaves
    var m:=StandardMaterial3D.new()
    m.cull_mode=BaseMaterial3D.CULL_DISABLED
    m.vertex_color_use_as_albedo=true
    node.material_override=m
    world.add_child(node)

func pavers(world):
    var unit:=BoxMesh.new()
    unit.size=Vector3(.293,.045,.145)
    var layout:=MultiMesh.new()
    layout.transform_format=MultiMesh.TRANSFORM_3D
    layout.use_colors=true
    layout.mesh=unit
    var cells:Array[Transform3D]=[]
    var tones:Array[Color]=[]
    for row in 454:
        for col in 35:
            var x:float=-5.+col*.30+(.075 if row%2==0 else -.075)
            var z:float=10.07+row*.15
            var left:=maxf(-5.,x-.1465)
            var right:=minf(5.,x+.1465)
            if right-left<.02:continue
            var hollow:float=(sin(z*.47+x*.8)+sin(x*2.-z*.23))*.0036
            var tilt:=Basis.from_euler(Vector3(rng.randf_range(-.018,.018),0,rng.randf_range(-.013,.013)))
            tilt=tilt.scaled_local(Vector3((right-left)/.293,1,1))
            cells.append(Transform3D(tilt,Vector3((left+right)*.5,.031+hollow,z)))
            tones.append(Color("bcae99").lerp(Color("d4c9af"),rng.randf()).srgb_to_linear())
    layout.instance_count=cells.size()
    for i in cells.size():
        layout.set_instance_transform(i,cells[i])
        layout.set_instance_color(i,tones[i])
    var node:=MultiMeshInstance3D.new()
    node.multimesh=layout
    var stone:=ShaderMaterial.new()
    stone.shader=preload("res://samples/anime_library/paver.gdshader")
    node.material_override=stone
    world.add_child(node)

