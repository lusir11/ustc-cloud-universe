extends RefCounted
# Props for the library frontage; all dimensions in metres.
func raised_panel(world, at:Vector3, size:Vector3, material:Material):
    var mesh:=BoxMesh.new()
    mesh.size=size
    var piece:=MeshInstance3D.new()
    piece.mesh=mesh
    piece.material_override=material
    piece.position=at
    world.add_child(piece)

func lettering(world, at:Vector3, text:String, height:float, ink:Color):
    var label:=Label3D.new()
    label.text=text
    label.font_size=80
    label.pixel_size=height/80.
    label.outline_size=0
    label.modulate=ink
    label.position=at
    world.add_child(label)

func light_material(color:Color,power:float)->StandardMaterial3D:
    var mat:=StandardMaterial3D.new()
    mat.albedo_color=color
    mat.emission_enabled=true
    mat.emission=color
    mat.emission_energy_multiplier=power
    return mat

func build(world,garden,real:bool):
    var glow:=light_material(Color("ffd59a"),1.9 if real else 1.5)
    # Light boxes sit behind the ground-floor glazing; offset from the door openings.
    for side in [-1,1]:
        for i in 3:
            raised_panel(world,Vector3(side*(2.7+i*1.1),7.53 if real else 5.73,-3.6 if real else -1.2),Vector3(.45,.035,.14) if real else Vector3(.82,.07,.5),glow)
    if real:
        for side in [-1,1]:
            for z in [25.,41.,59.]:
                var x:float=side*5.54
                world.block(Vector3(x,.099,z),Vector3(.55,.025,.69),"494841")
                for k in 7:
                    world.block(Vector3(x,.116,z-.27+k*.088),Vector3(.44,.009,.035),"242a2a")
        # Utilitarian bike hoops anchor the parking bay.
        for k in 5:
            var x:float=18.29+k*.88
            for z in [6.10,7.18]:
                world.block(Vector3(x,.38,z),Vector3(.055,.76,.055),"747c79")
            world.block(Vector3(x,.76,6.64),Vector3(.055,.055,1.1),"8d9592")
    var font_ink:=Color("fff1d3")
    for side in [-1,1]:
        var x:float=side*6.99
        var z:float=34 if side>0 else 25
        world.block(Vector3(x,1.61,z),Vector3(.095,3.22,.095),"304e54")
        var panel_x:float=x-side*.55
        world.block(Vector3(panel_x,3.12,z),Vector3(1.17,.065,.08),"354c52")
        world.block(Vector3(panel_x,2.36,z),Vector3(1.01,1.43,.065),"1d6974" if side>0 else "a95c43")
        lettering(world,Vector3(panel_x,2.74,z+.042),"LIBRARY",.145,font_ink)
        lettering(world,Vector3(panel_x,2.30,z+.042),"01" if side>0 else "02",.42,font_ink)
        world.block(Vector3(panel_x,1.81,z+.038),Vector3(.76,.036,.02),"f0ce86")
        garden.solid(Vector3(x,1.55,z),Vector3(.12,3.1,.12))
    for i in range(0 if real else 3):
        raised_panel(world,Vector3(0,12.01,1.1+i*.97),Vector3(12.4,.035,.09),glow)
