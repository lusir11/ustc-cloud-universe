shader_type spatial;
uniform sampler2D brick : source_color,repeat_enable,filter_linear_mipmap_anisotropic;
uniform sampler2D bump : hint_normal,repeat_enable,filter_linear_mipmap_anisotropic;
uniform vec3 brick_multiplier=vec3(.78,.54,.48);
varying vec3 p;
varying vec3 face;
void vertex(){p=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz; face=MODEL_NORMAL_MATRIX*NORMAL;}
float hash(vec2 n){return fract(sin(dot(n,vec2(71.2,137.7)))*4375.093);}
float noise2(vec2 n){vec2 i=floor(n),f=fract(n);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);}
void fragment(){
 vec2 uv=abs(face.x)>abs(face.z)?p.zy:p.xy;
 if(abs(face.y)>.75){uv=p.xz;}
 vec3 tex=texture(brick,uv*vec2(.48,.55)).rgb;
 float streak=noise2(uv*vec2(3.8,.08))*.6+noise2(uv*vec2(.83,.27))*.4;
 float patina=(1.-smoothstep(.3,2.7,p.y))*.33+smoothstep(.62,.89,streak)*.22;
 ALBEDO=mix(tex*brick_multiplier,vec3(.09,.087,.068),patina);
 NORMAL_MAP=texture(bump,uv*vec2(.48,.55)).rgb;
 NORMAL_MAP_DEPTH=.72; ROUGHNESS=mix(.88,.68,patina);
}
