shader_type spatial;
uniform sampler2D base : source_color,filter_linear_mipmap_anisotropic,repeat_enable;
uniform sampler2D normal_tex : hint_normal,filter_linear_mipmap_anisotropic,repeat_enable;
uniform vec4 tint : source_color = vec4(1.);
uniform float metres=2.7;
uniform bool road=false;
uniform bool cross_street=false;
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
  float curb=cross_street?abs(pos.y-15.)*5./3.:abs(pos.x);
  float low=noise2(pos*vec2(1.1,.35))*.32+noise2(pos*vec2(.36,.16))*.68;
  low+=smoothstep(2.3,4.8,curb)*.19;
  if(realistic){
   wet=smoothstep(.56,.72,low)*smoothstep(2.6,4.2,curb);
   float repair=abs(curb-3.12-noise2(vec2(floor(pos.y*.28),1.))*.42);
   ground*=1.-.33*(1.-smoothstep(.018,.06+fwidth(curb),repair));
  }else{
   vec2 grid=pos/vec2(1.45,2.1);
   grid.x+=mod(floor(grid.y),2.)*.5;
   vec2 edge=(.5-abs(fract(grid)-.5))*vec2(1.45,2.1);
   float seam=min(edge.x,edge.y);
   ground=tint.rgb*(.79+.13*hash(floor(grid))+.08*variation);
   ground*=mix(.50,1.,smoothstep(.006,.022+fwidth(seam),seam));
   wet=smoothstep(.72,.80,low)*smoothstep(4.35,4.9,curb)*.55;
  }
 }
 ALBEDO=mix(ground,ground*.37,wet);
 ROUGHNESS=mix(.91,.075,wet);
 SPECULAR=mix(.28,.9,wet);
 NORMAL_MAP=texture(normal_tex,uv).rgb;
 NORMAL_MAP_DEPTH=mix(realistic?.85:.09,.035,wet);
}
