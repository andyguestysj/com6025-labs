#version 330 core

out vec4 fragColor;

uniform vec3 emissive_color;

void main() {
  fragColor = vec4(emissive_color, 1.0);
}