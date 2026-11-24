shader_type spatial;
render_mode cull_disabled;
uniform vec4 pigment : source_color;
void fragment(){ALBEDO=pigment.rgb;ROUGHNESS=1.;}
void light(){
 float facing=dot(NORMAL,LIGHT);
 float band=.19+.49*smoothstep(-.15,.13,facing)+.32*smoothstep(.43,.60,facing);
 DIFFUSE_LIGHT+=ATTENUATION*LIGHT_COLOR*band/3.14159;
}
