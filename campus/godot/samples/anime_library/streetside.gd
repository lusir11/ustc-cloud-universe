extends RefCounted

func tube(world,a:Vector3,b:Vector3,r1:float,r2:float,color:String):
    var m:=CylinderMesh.new()
    m.bottom_radius=r1
    m.top_radius=r2
    m.height=a.distance_to(b)
    m.radial_segments=16
    var n:=MeshInstance3D.new()
    n.mesh=m
    n.material_override=world.paint(color)
    n.position=(a+b)*.5
    n.quaternion=Quaternion(Vector3.UP,a.direction_to(b))
    world.add_child(n)

func sign_text(world,pos:Vector3,words:String,size:float):
    var n:=Label3D.new()
    var font:=SystemFont.new()
    font.font_names=PackedStringArray(["Microsoft YaHei","Noto Sans CJK SC","sans-serif"])
    n.font=font
    n.text=words
    n.font_size=72
    n.pixel_size=size/72.
    n.outline_size=0
    n.modulate=Color("f2e9d3")
    n.position=pos
    world.add_child(n)

func install(world,garden):
    for side in [-1,1]:
        var p:=Vector3(side*7.44,0,31.5+side*3)
        tube(world,p,p+Vector3.UP*2.69,.055,.045,"6a7268")
        for i in 2:
            var at:=p+Vector3(.0,2.49-i*.33,0)
            world.block(at,Vector3(1.65,.30,.079),"31575b")
            sign_text(world,at+Vector3.BACK*.046,["↑  图书馆南门","↓  林荫步道"][i],.18)
        garden.solid(p+Vector3.UP,Vector3(.13,2,.13))
    # Mount housings on existing lamp posts, aimed down the path.
    for at in [Vector3(7.4,4.12,36.2),Vector3(-7.4,4.12,50.8)]:
        var arm:=Vector3(-signf(at.x)*.54,0,0)
        tube(world,at,at+arm,.042,.042,"586864")
        var head:Vector3=at+arm+Vector3.DOWN*.10
        var direction:=Vector3(-signf(at.x)*.36,-.35,.86).normalized()
        tube(world,head,head+direction*.45,.105,.115,"d6d2c5")
        tube(world,head+direction*.45,head+direction*.458,.088,.088,"24302e")
        tube(world,head+direction*.458,head+direction*.475,.043,.038,"425e66")
    for p in [Vector3(4.52,.044,22.5),Vector3(4.45,.044,24.),Vector3(4.56,.044,25.5),Vector3(-4.51,.044,20.7)]:
        world.block(p+Vector3.UP*.030,Vector3(.41,.06,.41),"413f38")
        var levels=[.058,.23,.31,.46,.52,.66]
        var rs=[.168,.134,.118,.088,.075,.046]
        for i in 5:
            tube(world,p+Vector3.UP*levels[i],p+Vector3.UP*levels[i+1],rs[i],rs[i+1],"d47037" if i%2==0 else "e8e2ce")
        garden.solid(p+Vector3.UP*.21,Vector3(.33,.42,.33))
    plant_beds(world)

func triangle(st:SurfaceTool,a:Vector3,b:Vector3,c:Vector3,col:Color):
    for v in [a,b,c]:
        st.set_color(col.srgb_to_linear())
        st.add_vertex(v)

func plant_beds(world):
    var rng:=RandomNumberGenerator.new()
    rng.seed=7319
    for kind in 3:
        var st:=SurfaceTool.new()
        st.begin(Mesh.PRIMITIVE_TRIANGLES)
        for j in 16:
            var angle:=j*2.39996
            var d:=Vector3(cos(angle),0,sin(angle))
            var side:=d.cross(Vector3.UP)
            var stem:=Vector3(rng.randf_range(-.13,.13),0,rng.randf_range(-.13,.13))
            var reach:=rng.randf_range(.28,.53)
            var length:=rng.randf_range(.33,.71)
            var green:=Color("3c6750").lerp(Color("849450"),rng.randf())
            for k in 7:
                var t:=k/7.
                var u:=(k+1)/7.
                var v:=stem+d*reach*t+Vector3.UP*length*sin(t*2.)
                var tip:=stem+d*reach*u+Vector3.UP*length*sin(u*2.)
                var width:=.005 if kind!=1 else .027*sin(.2+t*2.7)
                triangle(st,v-side*width,v+side*width,tip+side*width,green)
                triangle(st,v-side*width,tip+side*width,tip-side*width,green)
                if kind==0:
                    for sign_value in [-1.,1.]:
                        var leaf:Vector3=v+side*sign_value*.13*sin(.2+2.7*t)+d*.055
                        triangle(st,v,leaf,tip,green.lightened(.045))
                elif kind==2 and k>=4:
                    for l in 4:
                        var petal:=side*cos(l*PI/2)+d*sin(l*PI/2)
                        triangle(st,v-petal.cross(Vector3.UP)*.022,v+petal*.057+Vector3.UP*.029,v+petal.cross(Vector3.UP)*.022,Color("9687a2"))
        st.generate_normals()
        var instances:=MultiMesh.new()
        instances.transform_format=MultiMesh.TRANSFORM_3D
        instances.mesh=st.commit()
        instances.instance_count=72
        for j in 72:
            var side:float=1. if j%2 else -1.
            var z:float=21.+int(j/12)*9.+kind*1.32+rng.randf_range(-1.,1.)
            var at:=Vector3(side*rng.randf_range(7.88,9.12),.005,z)
            instances.set_instance_transform(j,Transform3D(Basis(Vector3.UP,rng.randf()*TAU).scaled_local(Vector3.ONE*rng.randf_range(.72,1.22)),at))
        var node:=MultiMeshInstance3D.new()
        var mat:=StandardMaterial3D.new()
        mat.vertex_color_use_as_albedo=true
        mat.cull_mode=BaseMaterial3D.CULL_DISABLED
        mat.roughness=.90
        node.material_override=mat
        node.multimesh=instances
        world.add_child(node)

