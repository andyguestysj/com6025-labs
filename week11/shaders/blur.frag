#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform sampler2D scene_tex;
uniform vec2 texel_size;
uniform vec2 direction;

void main() {
  float weights[3] = float[](0.227027, 0.1945946, 0.1216216);
  vec3 result = texture(scene_tex, v_uv).rgb * weights[0];
  for (int i = 1; i < 3; i++) {
    vec2 offset = direction * texel_size * float(i) * 1.5;
    result += texture(scene_tex, v_uv + offset).rgb * weights[i];
    result += texture(scene_tex, v_uv - offset).rgb * weights[i];
  }
  fragColor = vec4(result, 1.0);
}