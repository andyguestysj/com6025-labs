#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform sampler2D scene_tex;
uniform vec2 texel_size;

float luminance(vec3 c) {
  return dot(c, vec3(0.299, 0.587, 0.114));
}

void main() {
  float tl = luminance(texture(scene_tex, v_uv + vec2(-1, -1) * texel_size).rgb);
  float tr = luminance(texture(scene_tex, v_uv + vec2( 1, -1) * texel_size).rgb);
  float bl = luminance(texture(scene_tex, v_uv + vec2(-1,  1) * texel_size).rgb);
  float br = luminance(texture(scene_tex, v_uv + vec2( 1,  1) * texel_size).rgb);
  float l  = luminance(texture(scene_tex, v_uv + vec2(-1,  0) * texel_size).rgb);
  float r  = luminance(texture(scene_tex, v_uv + vec2( 1,  0) * texel_size).rgb);
  float t  = luminance(texture(scene_tex, v_uv + vec2( 0, -1) * texel_size).rgb);
  float b  = luminance(texture(scene_tex, v_uv + vec2( 0,  1) * texel_size).rgb);

  float gx = -tl - 2.0 * l - bl + tr + 2.0 * r + br;
  float gy = -tl - 2.0 * t - tr + bl + 2.0 * b + br;
  float edge = sqrt(gx * gx + gy * gy);

  fragColor = vec4(vec3(edge), 1.0);
}