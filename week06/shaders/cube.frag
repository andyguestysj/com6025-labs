#version 330 core

in vec3 v_color;
in vec2 v_uv;
in vec3 v_normal;
in vec3 v_frag_pos;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 light_dir;      // direction the light travels, world space
uniform vec3 light_color;
uniform vec3 view_pos;
uniform float ambient_strength;
uniform float shininess;

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

  fragColor = vec4(ambient + diffuse + specular, 1.0);
}