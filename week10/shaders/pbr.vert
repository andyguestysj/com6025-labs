#version 330 core

in vec3 in_position;
in vec3 in_normal;
in vec3 in_tangent;
in vec2 in_uv;

out vec2 v_uv;
out vec3 v_frag_pos;
out mat3 v_TBN;

uniform mat4 m_model;
uniform mat4 m_view;
uniform mat4 m_proj;

void main() {
  vec4 world_pos = m_model * vec4(in_position, 1.0);
  gl_Position = m_proj * m_view * world_pos;

  mat3 normal_matrix = mat3(transpose(inverse(m_model)));
  vec3 N = normalize(normal_matrix * in_normal);
  vec3 T = normalize(normal_matrix * in_tangent);
  T = normalize(T - dot(T, N) * N);   // re-orthogonalise against N (Gram-Schmidt)
  vec3 B = cross(N, T);
  v_TBN = mat3(T, B, N);

  v_frag_pos = world_pos.xyz;
  v_uv = in_uv;
}