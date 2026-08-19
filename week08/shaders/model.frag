#version 330 core

in vec3 v_color;
in vec2 v_uv;
in vec3 v_normal;
in vec3 v_frag_pos;

out vec4 fragColor;

struct PointLight {
  vec3 position;
  vec3 color;
  float constant;
  float linear;
  float quadratic;
};

struct SpotLight {
  vec3 position;
  vec3 direction;
  vec3 color;
  float cutoff;         // cos(inner angle)
  float outer_cutoff;   // cos(outer angle)
  float constant;
  float linear;
  float quadratic;
};

struct Material {
  float shininess;
};

#define NUM_POINT_LIGHTS 2

uniform sampler2D tex0;
uniform PointLight point_lights[NUM_POINT_LIGHTS];
uniform SpotLight spot_light;
uniform Material material;
uniform vec3 view_pos;

vec3 calc_point_light(PointLight light, vec3 N, vec3 V, vec3 albedo) {
  vec3 L = normalize(light.position - v_frag_pos);
  vec3 H = normalize(L + V);

  float dist = length(light.position - v_frag_pos);
  float attenuation = 1.0 / (light.constant + light.linear * dist + light.quadratic * dist * dist);

  vec3 ambient = 0.05 * light.color * albedo;
  float diff = max(dot(N, L), 0.0);
  vec3 diffuse = diff * light.color * albedo;
  float spec = pow(max(dot(N, H), 0.0), material.shininess);
  vec3 specular = spec * light.color;

  return (ambient + diffuse + specular) * attenuation;
}

vec3 calc_spot_light(SpotLight light, vec3 N, vec3 V, vec3 albedo) {
  vec3 L = normalize(light.position - v_frag_pos);
  float theta = dot(L, normalize(-light.direction));
  float intensity = smoothstep(light.outer_cutoff, light.cutoff, theta);

  float dist = length(light.position - v_frag_pos);
  float attenuation = 1.0 / (light.constant + light.linear * dist + light.quadratic * dist * dist);

  vec3 H = normalize(L + V);
  float diff = max(dot(N, L), 0.0);
  vec3 diffuse = diff * light.color * albedo;
  float spec = pow(max(dot(N, H), 0.0), material.shininess);
  vec3 specular = spec * light.color;

  return (diffuse + specular) * attenuation * intensity;
}

void main() {
  vec3 albedo = texture(tex0, v_uv).rgb * v_color;
  vec3 N = normalize(v_normal);
  vec3 V = normalize(view_pos - v_frag_pos);

  vec3 result = vec3(0.0);
  for (int i = 0; i < NUM_POINT_LIGHTS; i++) {
    result += calc_point_light(point_lights[i], N, V, albedo);
  }
  result += calc_spot_light(spot_light, N, V, albedo);

  fragColor = vec4(result, 1.0);
}