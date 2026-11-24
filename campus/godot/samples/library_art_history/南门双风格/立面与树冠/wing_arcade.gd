extends RefCounted

# Coordinates are metres in the library's local frame; positive Z faces the street.
func build(library:Node3D):
    var mats:Dictionary={}
    for part in library.find_children("*","MeshInstance3D",true,false):
        for i in part.mesh.get_surface_count():
            var m:Material=part.mesh.surface_get_material(i)
            if m:mats[m.resource_name.get_slice("Replica_",1)]=m
        var part_name:=str(part.name)
        if part_name.begins_with("FrontWindows") or part_name.begins_with("FrontFloorBands"):
            part.position.z+=1.22
    var brick:Material=mats["TerracottaBrick"]
    var stone:Material=mats["SilverPanel"]
    var base:Material=mats["RoseStone"]
    var soffit:Material=mats["Ceiling"]
    for hand in [-1,1]:
        panel(library,Vector3(hand*25.85,-.07,2.64),Vector3(20.8,.19,4.76),mats["StairStone"])
        for bay in 3:
            var x:float=hand*(15.7+(bay+.5)*6.7667)
            var front:float=[4.02,3.38,3.68][bay]
            # The glazing remains behind the cheeks. Head and sill close the returns.
            for level in 5:
                var y:float=3.6+level*3.73
                var edge:float=front if level==0 or level==4 else 2.25
                panel(library,Vector3(x,y,(edge+.4)*.5),Vector3(6.78,.70,edge-.4),brick if level==0 or level==4 else stone)
            panel(library,Vector3(x,3.22,(front+.43)*.5),Vector3(6.77,.09,front-.43),soffit)
            # Slight inset to the outer brick frame gives a second line of shadow.
            for sign_x in [-1,1]:
                var jamb:float=x+sign_x*2.83
                panel(library,Vector3(jamb,11.1,2.03),Vector3(.19,14.4,.70),stone)
            # End and intermediate piers terminate in full-depth returns.
            var axis:float=hand*(15.7+bay*6.7667)
            pier(library,axis,front,brick,base)
            if bay==2:pier(library,hand*36.0,front,brick,base)
            panel(library,Vector3(x,18.96,(front+.20)*.5),Vector3(6.78,1.12,front-.20),brick)
            panel(library,Vector3(x,19.56,(front+.20)*.5),Vector3(6.80,.11,front-.17),stone)

func pier(lib:Node3D,x:float,front:float,brick:Material,base:Material):
    panel(lib,Vector3(x,11.28,(front+.18)*.5),Vector3(1.05,16.1,front-.18),brick)
    panel(lib,Vector3(x,1.58,front-.60),Vector3(.76,3.16,.82),base)
    panel(lib,Vector3(x,.14,front-.60),Vector3(.88,.28,.94),base)
    panel(lib,Vector3(x,3.12,front-.60),Vector3(.94,.22,1.),base)

func panel(lib:Node3D,pos:Vector3,size:Vector3,mat:Material):
    var mesh:=BoxMesh.new()
    mesh.size=size
    mesh.material=mat
    var piece:=MeshInstance3D.new()
    piece.mesh=mesh
    piece.position=pos
    lib.add_child(piece)


