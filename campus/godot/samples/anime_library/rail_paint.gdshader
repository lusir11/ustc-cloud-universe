shader_type spatial;
varying vec3 w;
varying vec3 n;
void vertex(){w=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;n=MODEL_NORMAL_MATRIX*NORMAL;}
void fragment(){
 float streak=.5+.5*sin(w.z*4.7+sin(w.z*10.1)*.65+w.x*.8);
 float crown=smoothstep(.34,.99,normalize(n).y);
 float fade=crown*(.39+.51*streak);
 ALBEDO=mix(vec3(.145,.155,.145),vec3(.39,.31,.17),fade);
 ROUGHNESS=mix(.54,.77,fade);METALLIC=.22;
}
