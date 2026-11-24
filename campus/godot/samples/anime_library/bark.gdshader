shader_type spatial;
uniform sampler2D bark : source_color,repeat_enable,filter_linear_mipmap_anisotropic;
uniform sampler2D relief : hint_normal,repeat_enable,filter_linear_mipmap_anisotropic;
uniform vec4 bark_tone : source_color;
varying vec3 local_pos;
varying vec3 local_norm;
void vertex(){ local_pos=VERTEX; local_norm=NORMAL; }
void fragment(){
 vec3 weights=pow(abs(normalize(local_norm)),vec3(4.)); weights/=max(dot(weights,vec3(1.)),.001);
 vec3 p=local_pos*vec3(.88,.53,.88);
 vec3 col=texture(bark,p.zy).rgb*weights.x+texture(bark,p.xz).rgb*weights.y+texture(bark,p.xy).rgb*weights.z;
 ALBEDO=mix(col,bark_tone.rgb,.20)*.87;
 float occlusion=smoothstep(.0,.95,local_pos.y);
 ALBEDO*=mix(.55,1.,occlusion);
 NORMAL_MAP=texture(relief,mix(p.zy,p.xy,weights.z)).rgb;NORMAL_MAP_DEPTH=.37;ROUGHNESS=.92;
}
