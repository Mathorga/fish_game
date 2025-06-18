#version 150 core

/**
Default shader for rendering the view, base point for others.
Optionally can use pyglet.sprite.fragment_source
**/

in vec4 vertex_colors;
in vec3 texture_coords;

uniform sampler2D sprite_texture;
uniform float dt;

out vec4 final_color;

void main() {
    final_color = texture(sprite_texture, texture_coords.xy) * vertex_colors;

    // Dips to red on long rendered frames.
    //final_color.gb *= (1.0 - (dt - 0.01) * 100.0);

    // Rotate colors.
    //final_color.rgb = final_color.gbr;

    // Black/white.
    //float brightness = (final_color.r + final_color.g + final_color.b) / 3.0;
    //final_color = vec4(brightness, brightness, brightness, final_color.a);

    // Shows current xy coords on top of real colors.
    //final_color.rg *= texture_coords.xy;

    // Negative colors.
    //final_color.rgb = 1.0 - final_color.rgb;

    // This may be completely useless.
    if (final_color.a < 0.01) {
        discard;
    }
}