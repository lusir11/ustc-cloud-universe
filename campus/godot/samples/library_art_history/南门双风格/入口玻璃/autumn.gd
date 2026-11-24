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
        world.block(spec[0],spec[1],"827f72" if world.realistic else "c5af92")
        garden.solid(spec[0],spec[1])
    world.block(Vector3(0,7.69,-3.95),Vector3(14.2,.15,8.),"e0d1b7")
    if world.realistic:
        for x in [-4.5,4.5]:
            world.block(Vector3(x,3.67,-5.55),Vector3(2.30,.98,.74),"706354")
            world.block(Vector3(x,4.19,-5.55),Vector3(2.44,.075,.85),"aba899")
            garden.solid(Vector3(x,3.7,-5.55),Vector3(2.44,1.06,.85))
        for i in 11:
            world.block(Vector3(-6.10+i*.27,5.33,-7.71),Vector3(.11,3.80,.075),"756c60")
    # A pedestrian-height noticeboard on the sheltered wall facing the cross street.
    world.block(Vector3(-25.85,1.58,.42),Vector3(3.25,1.04,.08),"555d56")
    world.block(Vector3(-25.85,1.58,.468),Vector3(3.19,.98,.022),"bbb59f")
    for col in 4:
        var sheet:=QuadMesh.new()
        sheet.size=Vector2(.46,.841) if col==3 else Vector2(.594,.841)
        var mat:=StandardMaterial3D.new()
        mat.albedo_texture=preload("res://samples/anime_library/library_elevation.jpg") if col==3 else PRINTS
        mat.roughness=.95
        if col<3:
            mat.uv1_scale=Vector3(1./3.,1.,1.)
            mat.uv1_offset=Vector3(col/3.,0,0)
        var print_node:=MeshInstance3D.new()
        print_node.mesh=sheet
        print_node.material_override=mat
        print_node.position=Vector3(-26.96+col*.75,1.58,.49)
        world.add_child(print_node)
    for x in [-3.8,3.8]:
        var light:=OmniLight3D.new()
        light.position=Vector3(x,7.1,-4.5)
        light.omni_range=5.8
        light.light_color=Color("f4e7d3")
        light.light_energy=.72
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
    # Outer brick cheeks of the two towers: wall plane z=.725. Keep foliage
    # inside the masonry bay, clear of the slot windows and covered gallery.
    var palette=[Color("376448"),Color("668343"),Color("ae9545"),Color("b2573f"),Color("873e4c")]
    for side in [-1,1]:
        var root_x:float=side*13.56
        var height:=5.65 if side<0 else 3.55
        var face:=.732
        world.block(Vector3(root_x,.055,1.15),Vector3(2.65,.11,.85),"615440")
        world.block(Vector3(root_x,.075,1.59),Vector3(2.72,.15,.065),"827c66")
        for edge in [-1,1]:
            world.block(Vector3(root_x+edge*1.34,.075,1.15),Vector3(.055,.15,.92),"827c66")
        for leader in 3:
            var phase:float=leader*1.9
            var fork_height:float=[.11,.57,1.06][leader]
            var base_x:float=root_x+side*sin(phase)*.10
            if leader>0:
                ivy_stem(stems,Vector3(root_x,.11,.758),Vector3(base_x,fork_height,.755),.021)
            var h:float=height*(1.-leader*.14)
            var last:=Vector3(base_x,fork_height,.755)
            for k in 56:
                var t:float=(k+1.)/56.
                var spine:=Vector3(base_x+side*((leader-1)*1.02*t+sin(t*6.+phase)*.32*t),fork_height+(h-fork_height)*t,face+.013)
                ivy_stem(stems,last,spine,.026-.019*t)
                last=spine
                if k<2 or k%2!=0 or rng.randf()<.33:continue
                var direction:float=1. if rng.randf()<.52 else -1.
                var reach:float=(.24+.84*sin(PI*t))*rng.randf_range(.65,1.16)
                var rise:=rng.randf_range(.28,1.17)
                var tip:=spine
                for j in 10:
                    var u:float=(j+1.)/10.
                    var shoot:=spine+Vector3(direction*reach*u,rise*u+.12*sin(u*PI),.003)
                    ivy_stem(stems,tip,shoot,.008-.005*u)
                    tip=shoot
                    for l in 2:
                        var loc:=tip+Vector3(rng.randf_range(-.055,.055),rng.randf_range(-.055,.055),rng.randf_range(.014,.043))
                        var sz:=rng.randf_range(.115,.19)*(1.-.32*u)
                        poses.append(Transform3D(Basis(Vector3.BACK,direction*.46+rng.randf_range(-.65,.65)).scaled_local(Vector3.ONE*sz),loc))
                        var autumn:=clampf(.13+.53*t+.19*u+.14*sin(phase+t*6.)+rng.randf_range(-.10,.10),0,.999)
                        var tone:=autumn*4.
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

func ivy_stem(mesh:SurfaceTool,a:Vector3,b:Vector3,width:float):
    var tangent:=(b-a).normalized()
    var edge:=Vector3(-tangent.y,tangent.x,0)*width
    for vertex in [a-edge,a+edge,b+edge,a-edge,b+edge,b-edge]:
        mesh.add_vertex(vertex)

func pavers(world):
    brick_strip(world,0.,5.,10.07,454,.031)

func sidewalks(world):
    for side in [-1,1]:
        brick_strip(world,side*6.25,1.17,20.10,385,.119)

func brick_strip(world,center:float,half:float,start:float,rows:int,elevation:float):
    var unit:=BoxMesh.new()
    unit.size=Vector3(.293,.045,.145)
    var layout:=MultiMesh.new()
    layout.transform_format=MultiMesh.TRANSFORM_3D
    layout.use_colors=true
    layout.mesh=unit
    var cells:Array[Transform3D]=[]
    var tones:Array[Color]=[]
    for row in rows:
        for col in range(ceili(half*2./.30)+2):
            var x:float=center-half+col*.30+(.075 if row%2==0 else -.075)
            var z:float=start+row*.15
            var left:=maxf(center-half,x-.1465)
            var right:=minf(center+half,x+.1465)
            if right-left<.02:continue
            var hollow:float=(sin(z*.47+x*.8)+sin(x*2.-z*.23))*.0036
            var tilt:=Basis.from_euler(Vector3(rng.randf_range(-.018,.018),0,rng.randf_range(-.013,.013)))
            tilt=tilt.scaled_local(Vector3((right-left)/.293,1,1))
            cells.append(Transform3D(tilt,Vector3((left+right)*.5,elevation+hollow,z)))
            var light:=Color("b8b1a1") if world.realistic else Color("d4c9af")
            var dark:=Color("9c988c") if world.realistic else Color("bcae99")
            tones.append(dark.lerp(light,rng.randf()).srgb_to_linear())
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


func rail_segment(world,material:Material,a:Vector3,b:Vector3,r:float):
    var cylinder:=CylinderMesh.new()
    cylinder.top_radius=r
    cylinder.bottom_radius=r
    cylinder.height=a.distance_to(b)
    cylinder.radial_segments=16
    var node:=MeshInstance3D.new()
    node.mesh=cylinder
    node.material_override=material
    node.quaternion=Quaternion(Vector3.UP,a.direction_to(b))
    node.position=(a+b)*.5
    world.add_child(node)

func handrails(world):
    var coating:=ShaderMaterial.new()
    coating.shader=preload("res://samples/anime_library/rail_paint.gdshader")
    for x in [-9.32,-2.5,2.5,9.32]:
        var bottom:=Vector3(x,1.31,10.73)
        var top:=Vector3(x,4.35,4.48)
        rail_segment(world,coating,bottom,top,.043)
        rail_segment(world,coating,top,top+Vector3.FORWARD*.48,.043)
        for i in 5:
            var at:=bottom.lerp(top,i/4.)
            rail_segment(world,coating,at-Vector3.UP*.43,at,.031)


