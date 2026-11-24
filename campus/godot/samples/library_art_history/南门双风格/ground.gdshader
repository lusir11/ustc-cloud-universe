shader_type spatial;
uniform sampler2D base : source_color,filter_linear_mipmap_anisotropic,repeat_enable;
uniform sampler2D normal_tex : hint_normal,filter_linear_mipmap_anisotropic,repeat_enable;
uniform vec4 tint : source_color = vec4(1.);
uniform float metres=2.7;
uniform bool road=false;
uniform bool realistic=false;
varying vec2 pos;
float hash(vec2 p){p=fract(p*vec2(.1031,.1030));p+=dot(p,p.yx+33.33);return fract((p.x+p.y)*p.x);}
float noise2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1)),f.x),f.y);}
void vertex(){pos=(MODEL_MATRIX*vec4(VERTEX,1.)).xz;}
void fragment(){
 vec2 uv=pos/metres;
 vec3 tex=texture(base,uv).rgb;
 float variation=noise2(pos*.28)*.6+noise2(pos*.076)*.4;
 vec3 ground=tint.rgb*mix(vec3(1.),tex*2.2,realistic?.86:.42)*mix(.82,1.14,variation);
 float wet=0.;
 if(road){
  float curb=abs(pos.x);
  float low=noise2(pos*vec2(1.1,.35))*.32+noise2(pos*vec2(.36,.16))*.68;
  low+=smoothstep(2.3,4.8,curb)*.19;
  wet=smoothstep(.62,.685,low);
 }
 ALBEDO=mix(ground,ground*.37,wet);
 ROUGHNESS=mix(.91,.075,wet);
 SPECULAR=mix(.28,.9,wet);
 NORMAL_MAP=texture(normal_tex,uv).rgb;
 NORMAL_MAP_DEPTH=mix(realistic?.85:.35,.035,wet);
}
