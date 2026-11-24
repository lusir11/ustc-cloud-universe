shader_type spatial;
varying vec3 p;
uniform bool paint_bike=false;
uniform vec4 base_tone:source_color;
uniform vec4 accent:source_color;
void vertex(){p=VERTEX;}
void fragment(){
 float stripe=fract(p.x*3.4+p.y*1.6+p.z*.8);
 ALBEDO=mix(base_tone.rgb,accent.rgb,smoothstep(.60,.63,stripe)*(1.-smoothstep(.83,.86,stripe)));
 ROUGHNESS=.32; METALLIC=.24;
}
