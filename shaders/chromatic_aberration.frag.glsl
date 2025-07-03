#version 150

in vec4 vertex_colors;
in vec3 texture_coords;

uniform sampler2D sprite_texture;

vec2 mouseFocusPoint = vec2(0.5, 0.5);

out vec4 frag_color;

void main() {
  float red_offset = 0.012;
  float green_offset = 0.006;
  float blue_offset = -0.006;

  vec2 tex_size  = textureSize(sprite_texture, 0).xy;
//   vec2 tex_coord = gl_FragCoord.xy / tex_size;
  vec2 tex_coord = texture_coords.xy;

  vec2 direction = tex_coord - mouseFocusPoint;

  frag_color = texture(sprite_texture, tex_coord);

  frag_color.r = texture(sprite_texture, tex_coord + (direction * vec2(red_offset))).r;
  frag_color.g = texture(sprite_texture, tex_coord + (direction * vec2(green_offset))).g;
  frag_color.b = texture(sprite_texture, tex_coord + (direction * vec2(blue_offset))).b;
}