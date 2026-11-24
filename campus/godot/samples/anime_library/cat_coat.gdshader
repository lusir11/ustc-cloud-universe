shader_type spatial;
render_mode cull_disabled;
uniform bool calico;
uniform bool bib;
uniform sampler2D coat_normal:hint_normal,filter_linear_mipmap_anisotropic;
uniform sampler2D hairs:source_color,filter_linear_mipmap_anisotropic;
float patch(vec2 p,vec2 center,vec2 radius){
 vec2 q=(p-center)/radius;
 return 1.-smoothstep(.90,1.03,length(q));
}
void fragment(){
 vec2 p=UV2-vec2(.5,.4);
 p+=.006*vec2(sin(p.y*77.+p.x*101.),sin(p.x*111.+p.y*61.));
 float grain=dot(texture(hairs,UV).rgb,vec3(.30,.59,.11));
 vec3 fur=vec3(.020,.021,.025);
 if(calico){
  float ginger=max(patch(p,vec2(.058,-.28),vec2(.069,.086)),patch(p,vec2(-.063,.050),vec2(.112,.142)));
  ginger=max(ginger,patch(p,vec2(.067,.227),vec2(.095,.116)));
  float ink=max(patch(p,vec2(-.066,-.274),vec2(.063,.088)),patch(p,vec2(.085,-.054),vec2(.082,.116)));
  ink=max(ink,patch(p,vec2(-.040,.194),vec2(.098,.083)));
  if(p.y>.30){ink=max(ink,smoothstep(.30,.32,p.y));}
  fur=mix(mix(vec3(.79,.73,.61),vec3(.55,.192,.050),ginger),vec3(.026,.023,.022),ink);
  if(bib){fur=mix(fur,vec3(.80,.75,.66),.80);}
 }
 ALBEDO=fur*(.88+.36*grain);
 NORMAL_MAP=texture(coat_normal,UV).rgb;
 NORMAL_MAP_DEPTH=.32;
 ROUGHNESS=.82;
 RIM=.22; RIM_TINT=.65;
}
