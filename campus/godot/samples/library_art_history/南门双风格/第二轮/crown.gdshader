shader_type spatial;
render_mode cull_disabled;
uniform vec4 pigment:source_color;
varying vec3 local;
void vertex(){local=VERTEX;}
void fragment(){
 float strata=smoothstep(4.,13.,local.y);
 ALBEDO=pigment.rgb*mix(vec3(.66,.77,.86),vec3(1.08,1.06,.95),strata);
 ROUGHNESS=1.;
}
void light(){
 float n=dot(NORMAL,LIGHT);
 float tone=.15+.50*smoothstep(-.09,.04,n)+.35*smoothstep(.58,.66,n);
 DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*tone/3.14159;
}
