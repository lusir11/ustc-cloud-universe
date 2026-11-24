shader_type spatial;
uniform bool damp_avenue = false;
varying vec2 position_xz;
void vertex() {
    position_xz = (MODEL_MATRIX * vec4(VERTEX,1.0)).xz;
}
float hash2(vec2 p) {
    p = fract(p * vec2(.1031,.1030));
    p += dot(p,p.yx+33.33);
    return fract((p.x+p.y)*p.x);
}
float grain(vec2 point) {
    vec2 cell=floor(point), f=fract(point);
    f=f*f*(3.0-2.0*f);
    return mix(mix(hash2(cell),hash2(cell+vec2(1,0)),f.x),
               mix(hash2(cell+vec2(0,1)),hash2(cell+vec2(1,1)),f.x),f.y);
}
void fragment() {
    vec2 p=position_xz;
    float footprint=max(length(dFdx(p)),length(dFdy(p)));
    float flecks=(grain(p*370.)-.5)*(1.-smoothstep(.001,.005,footprint));
    float grit=(grain(p*96.)-.5)*(1.-smoothstep(.003,.020,footprint));
    float weather=grain(p*3.7)-.5;
    float wet=0.;
    if (damp_avenue) {
        float hollow=(sin(p.y*.47+p.x*.8)+sin(p.x*2.-p.y*.23))*.0036;
        wet=1.-smoothstep(-.0059,-.0038,hollow);
    }
    ALBEDO=COLOR.rgb*(1.+.24*flecks+.16*grit+.10*weather)*mix(1.,.68,wet);
    ROUGHNESS=clamp(.88+.1*grit+.06*weather-.55*wet,.25,.99);
    SPECULAR=mix(.27,.47,wet);
}
