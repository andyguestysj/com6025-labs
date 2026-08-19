#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform sampler2D scene_tex;

void main() {
  vec3 color = texture(scene_tex, v_uv).rgb;
  float grey = dot(color, vec3(0.299, 0.587, 0.114));
  fragColor = vec4(vec3(grey), 1.0);
}