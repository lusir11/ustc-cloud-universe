shader_type spatial;
render_mode cull_disabled, blend_mix, depth_draw_never;

void fragment() {
	// A clear pane passes the scene behind it. Only its surface tint and
	// the live environment reflection become prominent at grazing angles.
	float cosine = clamp(abs(dot(normalize(NORMAL), normalize(VIEW))), 0.0, 1.0);
	float fresnel = 0.078 + 0.922 * pow(1.0 - cosine, 5.0);
	ALBEDO = vec3(0.65, 0.79, 0.74);
	METALLIC = 0.0;
	SPECULAR = 0.55;
	ROUGHNESS = 0.065;
	ALPHA = min(0.92, 0.035 + fresnel);
}
