#version 330 core

in vec3 in_position;
in vec3 in_color;

out vec3 v_color;

uniform mat4 m_model;

void main() {
  gl_Position = m_model * vec4(in_position, 1.0);
  v_color = in_color;
}