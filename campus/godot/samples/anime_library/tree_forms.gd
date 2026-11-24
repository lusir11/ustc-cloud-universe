extends RefCounted

var urns:Dictionary={}
var prev:Dictionary={}
var rng:=RandomNumberGenerator.new()

func _init():
    rng.seed=11053

func pick(family:String)->PackedScene:
    if not urns.has(family) or urns[family].is_empty():
        var pool:Array=range(10)
        for i in range(9,0,-1):
            var j:=rng.randi_range(0,i)
            var old=pool[i]
            pool[i]=pool[j]
            pool[j]=old
        if pool.back()==prev.get(family,-1):
            var old=pool[9]
            pool[9]=pool[0]
            pool[0]=old
        urns[family]=pool
    var id:int=urns[family].pop_back()
    prev[family]=id
    return load("res://samples/anime_library/forms/%s_%d.glb"%[family,id])
