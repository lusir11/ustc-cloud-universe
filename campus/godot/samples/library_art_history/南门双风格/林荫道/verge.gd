extends RefCounted

const CEDAR=preload("res://assets/tree_conifer.glb")
const SHRUB=preload("res://assets/shrub.glb")

func build(world,garden):
    var rng:=RandomNumberGenerator.new()
    rng.seed=51383
    for row in 2:
        for i in 10:
            var cedar:Node3D=CEDAR.instantiate()
            var x:float=-9.4-row*5.4+rng.randf_range(-.75,.65)
            var z:float=13.+i*7.05+row*3.4+rng.randf_range(-.85,.85)
            cedar.position=Vector3(x,0,z)
            cedar.rotation.y=rng.randf()*TAU
            cedar.scale=Vector3(1.33,1.43,1.35)*rng.randf_range(.92,1.16)
            world.add_child(cedar)
            garden.solid(Vector3(x,1.25,z),Vector3(.55,2.5,.55))
    for side in [-1,1]:
        for base in [25.,52.,65.]:
            var x:float=side*7.57
            for k in 4:
                var z:float=base+k*1.62
                world.block(Vector3(x,.37,z),Vector3(.062,.74,.062),"3c514b")
                world.block(Vector3(x,.756,z),Vector3(.088,.032,.088),"9b9880")
            for y in [.30,.66]:
                world.block(Vector3(x,y,base+2.43),Vector3(.045,.048,4.86),"526b62")
            garden.solid(Vector3(x,.38,base+2.43),Vector3(.08,.76,4.90))
            for j in 7:
                var shrub:Node3D=SHRUB.instantiate()
                shrub.position=Vector3(x+side*rng.randf_range(.65,1.05),-.12,base-.4+j*.94)
                shrub.rotation.y=rng.randf()*TAU
                shrub.scale=Vector3(.66,.88,.77)*rng.randf_range(.78,1.13)
                world.add_child(shrub)
