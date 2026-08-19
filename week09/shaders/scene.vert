#version 330 core

in vec3 in_position;
in vec3 in_color;
in vec3 in_normal;
in vec2 in_uv;

out vec3 v_color;
out vec2 v_uv;
out vec3 v_normal;
out vec3 v_frag_pos;
out vec4 v_frag_pos_light_space;

uniform mat4 m_model;
uniform mat4 m_view;
uniform mat4 m_proj;
uniform mat4 light_space_matrix;

void main() {
  vec4 world_pos = m_model * vec4(in_position, 1.0);
  gl_Position = m_proj * m_view * world_pos;

  mat3 normal_matrix = mat3(transpose(inverse(m_model)));
  v_normal = normalize(normal_matrix * in_normal);
  v_frag_pos = world_pos.xyz;
  v_frag_pos_light_space = light_space_matrix * world_pos;

  v_color = in_color;
  v_uv = in_uv;
}