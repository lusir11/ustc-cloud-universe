extends CharacterBody3D

var eye := Camera3D.new()
var heading := 0.0
var pitch := deg_to_rad(9.5)

func _ready():
    var capsule := CapsuleShape3D.new()
    capsule.radius=.30
    capsule.height=1.73
    var collider := CollisionShape3D.new()
    collider.shape=capsule
    collider.position.y=.865
    add_child(collider)
    floor_snap_length=.28
    eye.position.y=1.68
    eye.fov=62
    add_child(eye)
    eye.current=true
    eye.rotation.x=pitch

func _unhandled_input(e):
    if e is InputEventMouseButton and e.button_index==MOUSE_BUTTON_LEFT and e.pressed:
        Input.mouse_mode=Input.MOUSE_MODE_CAPTURED
    elif e is InputEventKey and e.keycode==KEY_ESCAPE and e.pressed:
        Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
    elif e is InputEventMouseMotion and Input.mouse_mode==Input.MOUSE_MODE_CAPTURED:
        heading-=e.relative.x*.0024
        pitch=clampf(pitch-e.relative.y*.0024,-1.42,1.42)
        rotation.y=heading
        eye.rotation.x=pitch

func _physics_process(dt):
    var axis:=Vector3(float(Input.is_key_pressed(KEY_D))-float(Input.is_key_pressed(KEY_A)),0,float(Input.is_key_pressed(KEY_S))-float(Input.is_key_pressed(KEY_W)))
    var travel:=transform.basis*axis.normalized()*(5.3 if Input.is_key_pressed(KEY_SHIFT) else 2.9)
    velocity.x=travel.x
    velocity.z=travel.z
    if not is_on_floor():
        velocity.y-=20*dt
    elif Input.is_key_pressed(KEY_SPACE):
        velocity.y=5.0
    move_and_slide()
