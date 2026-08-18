#version 330 core

in vec3 v_color;
in vec2 v_uv;

out vec4 fragColor;

uniform sampler2D tex0;
uniform sampler2D tex1;

void main() {
  vec4 diffuse = texture(tex0, v_uv);
  vec4 detail = texture(tex1, v_uv * 4.0);
  vec3 combined = diffuse.rgb * detail.rgb * v_color;
  fragColor = vec4(combined, diffuse.a);
}