#version 330 core

in vec3 v_color;
in vec2 v_uv;
in vec3 v_normal;
in vec3 v_frag_pos;
in vec4 v_frag_pos_light_space;

out vec4 fragColor;

uniform sampler2D tex0;
uniform sampler2D shadow_map;
uniform vec3 light_dir;
uniform vec3 light_color;
uniform vec3 view_pos;
uniform float ambient_strength;
uniform float shininess;

float calc_shadow(vec4 frag_pos_light_space, vec3 N, vec3 L) {
  vec3 proj_coords = frag_pos_light_space.xyz / frag_pos_light_space.w;
  proj_coords = proj_coords * 0.5 + 0.5;

  if (proj_coords.z > 1.0) {
    return 0.0;
  }

  float current_depth = proj_coords.z;
  float bias = max(0.005 * (1.0 - dot(N, L)), 0.0015);
  float closest_depth = texture(shadow_map, proj_coords.xy).r;

  //float shadow = (current_depth - bias) > closest_depth ? 1.0 : 0.0;

  vec2 texel_size = 1.0 / textureSize(shadow_map, 0);
  float shadow = 0.0;
  for (int x = -1; x <= 1; x++) {
    for (int y = -1; y <= 1; y++) {
      float pcf_depth = texture(shadow_map, proj_coords.xy + vec2(x, y) * texel_size).r;
      shadow += current_depth - bias > pcf_depth ? 1.0 : 0.0;
    }
  }
  shadow /= 9.0;
  return shadow;

  return shadow;
}

void main() {
  vec3 albedo = texture(tex0, v_uv).rgb * v_color;

  vec3 N = normalize(v_normal);
  vec3 L = normalize(-light_dir);
  vec3 V = normalize(view_pos - v_frag_pos);
  vec3 H = normalize(L + V);

  vec3 ambient = ambient_strength * light_color * albedo;

  float diff = max(dot(N, L), 0.0);
  vec3 diffuse = diff * light_color * albedo;

  float spec = pow(max(dot(N, H), 0.0), shininess);
  vec3 specular = spec * light_color;

  float shadow = calc_shadow(v_frag_pos_light_space,N, L);

  fragColor = vec4(ambient + (1.0 - shadow) * (diffuse + specular), 1.0);
}