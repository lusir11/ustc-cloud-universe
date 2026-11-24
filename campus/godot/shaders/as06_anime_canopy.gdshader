shader_type spatial;
render_mode cull_disabled, specular_disabled;

uniform sampler2D sprays : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
varying vec3 canopy_normal_view;
varying float height_light;

void vertex() {
	// The broad flowering boughs catch skylight as volumes. Preserve the
	// fine silhouette without lighting each thin spray as a flat sheet.
	height_light = smoothstep(3.3, 6.9, VERTEX.y);
	vec2 radius = VERTEX.xz / max(length(VERTEX.xz), 0.4);
	vec3 crown_normal = normalize(vec3(radius.x * 0.74, 0.56 + height_light, radius.y * 0.74));
	canopy_normal_view = MODELVIEW_NORMAL_MATRIX * crown_normal;
}

void fragment() {
	vec4 spray = texture(sprays, UV);
	ALPHA = spray.a;
	ALPHA_SCISSOR_THRESHOLD = 0.40;
	NORMAL = normalize(canopy_normal_view + 0.18 * NORMAL);
	ALBEDO = spray.rgb * mix(vec3(0.87, 0.74, 0.96), vec3(1.03, 0.99, 1.00), height_light);
	ROUGHNESS = 1.0;
	EMISSION = ALBEDO * (0.045 + 0.045 * height_light);
}

void light() {
	float diffuse = smoothstep(-0.42, 0.85, dot(NORMAL, LIGHT));
	vec3 tone = mix(vec3(0.43, 0.34, 0.57), vec3(1.0, 0.98, 1.0), diffuse);
	DIFFUSE_LIGHT += 0.59 * LIGHT_COLOR * tone * mix(0.32, 1.0, ATTENUATION) / PI;
}
