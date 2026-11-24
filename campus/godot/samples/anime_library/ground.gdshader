shader_type spatial;
uniform sampler2D base : source_color,filter_linear_mipmap_anisotropic,repeat_enable;
uniform sampler2D normal_tex : hint_normal,filter_linear_mipmap_anisotropic,repeat_enable;
uniform vec4 tint : source_color = vec4(1.);
uniform float metres=2.7;
uniform bool road=false;
uniform bool pool_surface=false;
uniform bool cross_street=false;
uniform bool realistic=false;
varying vec2 pos;
float hash(vec2 p){p=fract(p*vec2(.1031,.1030));p+=dot(p,p.yx+33.33);return fract((p.x+p.y)*p.x);}
float noise2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1)),f.x),f.y);}
// Local depressions in metres. The same height field shapes the asphalt and
// intersects the level water plane 12 mm below the nominal road surface.
float pocket(vec2 offset, vec2 radius, float depth){
 vec2 q=offset/radius;
 if(abs(q.y)>1.35 || abs(q.x)>1.7){return 0.;}
 float bend=.26*q.y+.18*(1.-q.y*q.y);
 float width=1.-.26*q.y+.13*sin(q.y*4.);
 float across=(q.x-bend)/width;
 float ragged=(noise2(offset*5.+radius*11.)-.5)*.22;
 float edge=length(vec2(across,q.y))+ragged;
 return depth*(1.-smoothstep(.14,1.26,edge));
}
float basin(vec2 w){
 if(cross_street){
  return pocket(w.yx-vec2(12.32,-22.8),vec2(.31,1.02),.021);
 }
 if(w.x<0.){
  return pocket(w-vec2(-4.59,31.4),vec2(.37,.94),.020);
 }
 vec2 edge=w-vec2(4.74,50.35);
 float main_bed=pocket(edge,vec2(.27,1.85),.025);
 float lip=pocket(edge-vec2(-.17,.80),vec2(.21,.68),.018);
 return max(main_bed,lip);
}
void vertex(){
 pos=(MODEL_MATRIX*vec4(VERTEX,1.)).xz;
 if(road && realistic && !pool_surface){VERTEX.y-=basin(pos);}
}
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
   vec2 lane=cross_street?vec2(pos.y-15.,pos.x):pos;
   float hw=cross_street?3.:5.;
   float depth=basin(pos);
   wet=smoothstep(.001,.018,depth);
   float paint_noise=noise2(pos*58.);
   float boundary=(noise2(pos*23.)-.5)*.021;
   float aa=max(.002,min(.04,fwidth(lane.x)));
   float center=1.-smoothstep(.065-aa,.065+aa,abs(lane.x)+boundary);
   float dash=abs(mod(lane.y+1.,6.)-3.);
   center*=1.-smoothstep(1.49,1.52,dash);
   float edge=1.-smoothstep(.055-aa,.055+aa,abs(abs(lane.x)-(hw-.36))+boundary);
   if(cross_street && abs(pos.x)<5.1 && lane.x>0.){edge=0.;}
   if(!cross_street && pos.y<19.){edge=0.;center=0.;}
   float crack=abs(fract(lane.y*.83+noise2(pos*4.)*.16+lane.x*.48)-.5);
   float coverage=mix(.66,.91,paint_noise)*smoothstep(.006,.026,crack);
   coverage*=mix(.58,1.,smoothstep(.15,.48,paint_noise));
   ground=mix(ground,vec3(.52,.322,.063),center*coverage);
   ground=mix(ground,vec3(.63,.61,.55),edge*coverage);
   if(pool_surface && depth<.012){discard;}
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
 ALBEDO=mix(ground,ground*.57,wet);
 ROUGHNESS=pool_surface?.13:mix(.91,.53,wet);
 SPECULAR=pool_surface?.46:mix(.28,.39,wet);
 NORMAL_MAP=texture(normal_tex,uv).rgb;
 NORMAL_MAP_DEPTH=pool_surface?0.:mix(realistic?.85:.09,.035,wet);
}
