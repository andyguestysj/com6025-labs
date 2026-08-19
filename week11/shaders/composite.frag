#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform sampler2D scene_tex;
uniform sampler2D bloom_tex;
uniform float bloom_intensity;

void main() {
  vec3 scene_color = texture(scene_tex, v_uv).rgb;
  vec3 bloom_color = texture(bloom_tex, v_uv).rgb;
  vec3 result = scene_color + bloom_color * bloom_intensity;
  result = result / (result + vec3(1.0));
  fragColor = vec4(result, 1.0);
}