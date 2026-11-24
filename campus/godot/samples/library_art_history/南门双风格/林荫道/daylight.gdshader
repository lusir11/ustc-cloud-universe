shader_type sky;

// A fixed cloud field is integrated into the sky radiance map once.
float hash3(vec3 p){
 p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z);
}
float noise3(vec3 p){
 vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
 vec4 n=vec4(hash3(i),hash3(i+vec3(0,1,0)),hash3(i+vec3(0,0,1)),hash3(i+vec3(0,1,1)));
 vec4 m=vec4(hash3(i+vec3(1,0,0)),hash3(i+vec3(1,1,0)),hash3(i+vec3(1,0,1)),hash3(i+vec3(1,1,1)));
 vec4 a=mix(n,m,f.x);return mix(mix(a.x,a.y,f.y),mix(a.z,a.w,f.y),f.z);
}
float field(vec3 p){
 vec2 q=p.xz+vec2(2.0,-.8);
 float bank=noise3(vec3(q*.35,.35))*.60+noise3(vec3(q*.91,2.2))*.40;
 float billow=noise3(p*1.9)*.24+noise3(p*4.2)*.105+noise3(p*9.3)*.071+noise3(p*18.5)*.029;
 float envelope=abs(p.y-2.0)*.30;
 return max(0.,(bank+billow-.625-envelope)*5.5);
}
vec3 atmosphere(vec3 ray){
 float h=max(ray.y,0.);
 vec3 blue=mix(vec3(.20,.47,.69),vec3(.028,.225,.59),smoothstep(0.,.46,h));
 blue=mix(blue,vec3(.019,.13,.42),smoothstep(.46,1.,h));
 if(h<.035){return blue;}
 float start=1.05/h, end=min(3.10/h,23.);
 float step_len=max(end-start,0.)/40.;
 float trans=1.;vec3 light=vec3(0.);
 for(int i=0;i<40;i++){
  vec3 p=ray*(start+(float(i)+.5)*step_len);
  float d=field(p);
  if(d>.001){
   vec3 sun=vec3(-.52,.74,.42);
   float shadow=field(p+sun*.35)*.8+field(p+sun*.82)*.45;
   float lit=exp(-shadow*2.6)*(.65+.35*smoothstep(1.25,2.65,p.y));
   vec3 scatter=mix(vec3(.16,.235,.35),vec3(.95,.90,.82),lit);
   float absorb=1.-exp(-d*step_len*6.2);
   light+=trans*absorb*scatter;trans*=1.-absorb;
   if(trans<.016){break;}
  }
 }
 return mix(blue,light+trans*blue,smoothstep(.035,.11,h));
}
void sky(){
 if(AT_CUBEMAP_PASS){COLOR=atmosphere(EYEDIR);}
 else{COLOR=textureLod(RADIANCE,EYEDIR,0.).rgb;}
}

