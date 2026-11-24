shader_type sky;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.55);}
float noise2(vec2 p){
 vec2 i=floor(p); vec2 f=fract(p); f=f*f*(3.0-2.0*f);
 return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1)),f.x),f.y);
}
void sky(){
 float h=max(EYEDIR.y,0.0);
 vec3 c=mix(vec3(.72,.87,.97),vec3(.12,.43,.91),smoothstep(0.,.55,h));
 vec2 uv=EYEDIR.xz/max(h+.12,.12)*1.6;
 float n=noise2(uv)*.53+noise2(uv*2.1)*.28+noise2(uv*4.3)*.13+noise2(uv*8.7)*.06;
 float cloud=smoothstep(.52,.61,n)*smoothstep(.015,.12,h);
 COLOR=mix(c,mix(vec3(.76,.83,.92),vec3(1.,.97,.91),smoothstep(.54,.68,n)),cloud);
}
