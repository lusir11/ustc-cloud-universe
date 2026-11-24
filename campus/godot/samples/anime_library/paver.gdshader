shader_type spatial;
varying vec3 p;
void vertex(){p=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;}
void fragment(){
 float hollow=(sin(p.z*.47+p.x*.8)+sin(p.x*2.-p.z*.23))*.0036;
 float wet=(1.-smoothstep(-.0059,-.0038,hollow))*smoothstep(.5,3.9,abs(p.x));
 ALBEDO=COLOR.rgb*mix(1.,.54,wet);
 ROUGHNESS=mix(.86,.09,wet); SPECULAR=mix(.30,.87,wet);
}
