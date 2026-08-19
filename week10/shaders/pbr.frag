#version 330 core

in vec2 v_uv;
in vec3 v_frag_pos;
in mat3 v_TBN;

out vec4 fragColor;

uniform sampler2D tex_albedo;
uniform sampler2D tex_normal;
uniform sampler2D tex_roughness;
uniform sampler2D tex_metallic;
uniform sampler2D tex_ao;

uniform vec3 light_pos;
uniform vec3 light_color;
uniform vec3 view_pos;

const float PI = 3.14159265359;

float distribution_ggx(vec3 N, vec3 H, float roughness) {
  float a = roughness * roughness;
  float a2 = a * a;
  float NdotH = max(dot(N, H), 0.0);
  float NdotH2 = NdotH * NdotH;
  float denom = (NdotH2 * (a2 - 1.0) + 1.0);
  denom = PI * denom * denom;
  return a2 / max(denom, 0.0001);
}

float geometry_schlick_ggx(float NdotV, float roughness) {
  float r = roughness + 1.0;
  float k = (r * r) / 8.0;
  float denom = NdotV * (1.0 - k) + k;
  return NdotV / max(denom, 0.0001);
}

float geometry_smith(vec3 N, vec3 V, vec3 L, float roughness) {
  float NdotV = max(dot(N, V), 0.0);
  float NdotL = max(dot(N, L), 0.0);
  float ggx2 = geometry_schlick_ggx(NdotV, roughness);
  float ggx1 = geometry_schlick_ggx(NdotL, roughness);
  return ggx1 * ggx2;
}

vec3 fresnel_schlick(float cos_theta, vec3 F0) {
  return F0 + (1.0 - F0) * pow(clamp(1.0 - cos_theta, 0.0, 1.0), 5.0);
}

void main() {
  vec3 albedo = texture(tex_albedo, v_uv).rgb;
  float roughness = texture(tex_roughness, v_uv).r;
  float metallic = texture(tex_metallic, v_uv).r;
  float ao = texture(tex_ao, v_uv).r;

  vec3 tangent_normal = texture(tex_normal, v_uv).rgb * 2.0 - 1.0;
  vec3 N = normalize(v_TBN * tangent_normal);
  vec3 V = normalize(view_pos - v_frag_pos);

  vec3 F0 = mix(vec3(0.04), albedo, metallic);

  vec3 L = normalize(light_pos - v_frag_pos);
  vec3 H = normalize(V + L);
  float dist = length(light_pos - v_frag_pos);
  float attenuation = 1.0 / (dist * dist);
  vec3 radiance = light_color * attenuation;

  float NDF = distribution_ggx(N, H, roughness);
  float G = geometry_smith(N, V, L, roughness);
  vec3 F = fresnel_schlick(max(dot(H, V), 0.0), F0);

  vec3 numerator = NDF * G * F;
  float denom = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0) + 0.0001;
  vec3 specular = numerator / denom;

  vec3 kS = F;
  vec3 kD = (vec3(1.0) - kS) * (1.0 - metallic);

  float NdotL = max(dot(N, L), 0.0);
  vec3 Lo = (kD * albedo / PI + specular) * radiance * NdotL;

  vec3 ambient = vec3(0.03) * albedo * ao;
  vec3 color = ambient + Lo;

  color = color / (color + vec3(1.0));   // Reinhard tone mapping
  color = pow(color, vec3(1.0 / 2.2));   // gamma correction

  fragColor = vec4(color, 1.0);
}