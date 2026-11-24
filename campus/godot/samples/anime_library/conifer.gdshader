shader_type spatial;
render_mode cull_disabled;
uniform bool wood=false;
uniform vec4 tone:source_color;
varying vec3 local_position;
void vertex(){local_position=VERTEX;}
float hash(vec3 p){p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z);}
float noise3(vec3 p){
 vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
 vec4 a=vec4(hash(i),hash(i+vec3(0,1,0)),hash(i+vec3(0,0,1)),hash(i+vec3(0,1,1)));
 vec4 b=vec4(hash(i+vec3(1,0,0)),hash(i+vec3(1,1,0)),hash(i+vec3(1,0,1)),hash(i+vec3(1,1,1)));
 a=mix(a,b,f.x);return mix(mix(a.x,a.y,f.y),mix(a.z,a.w,f.y),f.z);
}
void fragment(){
 float bark=noise3(local_position*vec3(19.,1.8,19.));
 float cluster=noise3(local_position*1.45);
 float grain=noise3(local_position*vec3(24.,6.,24.));
 if(wood){
  float fissure=smoothstep(.46,.73,bark+.11*grain);
  ALBEDO=tone.rgb*(.58+.67*fissure+.25*cluster);
  NORMAL_MAP=vec3(.5+.16*(bark-.5),.5,.98);
  ROUGHNESS=.95;
 }else{
  ALBEDO=tone.rgb*(.69+.51*cluster+.24*grain)*mix(.70,1.08,smoothstep(3.,13.,local_position.y));
  BACKLIGHT=tone.rgb*.16;ROUGHNESS=.81;
 }
}

