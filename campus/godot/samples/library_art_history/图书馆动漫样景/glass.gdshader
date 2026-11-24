shader_type spatial;
render_mode cull_disabled;
void fragment(){
 vec3 ray=normalize((INV_VIEW_MATRIX*vec4(reflect(-VIEW,NORMAL),0.0)).xyz);
 float sky=smoothstep(-.14,.53,ray.y);
 vec3 tint=mix(vec3(.035,.11,.145),vec3(.17,.40,.63),sky);
 float ribbon=smoothstep(.73,.93,sin(ray.x*8.+ray.y*14.)*.5+.5)*smoothstep(.04,.3,ray.y);
 ALBEDO=tint; EMISSION=tint*.24+vec3(.035,.05,.062)*ribbon;
 ROUGHNESS=.24; SPECULAR=.55; ALPHA=.78;
}
