'''
Core Jackit Module. Defines vertext shader and fragment shader programs
'''

VERTEX_SHADER = '''
#version 330

uniform vec4 Camera;

// Per vertex
in vec2 in_vert;
in vec2 in_texture;

// Per instance
in vec3 in_pos;
in vec2 in_size;
in vec4 in_tint;

out vec2 v_vert;
out vec2 v_texture;
out vec4 v_tint;

void main() {
    mat2 rotate = mat2(
        cos(in_pos.z), sin(in_pos.z),
        -sin(in_pos.z), cos(in_pos.z)
    );
    v_vert = rotate * (in_vert * in_size) + in_pos.xy;
    gl_Position = vec4((v_vert - Camera.xy) / Camera.zw, 0.0, 1.0);
    v_texture = in_texture;
    v_tint = in_tint;
}
'''

FRAGMENT_SHADER = '''
#version 330

uniform sampler2D Texture;

in vec2 v_vert;
in vec2 v_texture;
in vec4 v_tint;

out vec4 f_color;

void main() {
    vec4 tex = texture(Texture, v_texture);
    vec3 color = tex.rgb * (1.0 - v_tint.a) + v_tint.rgb * v_tint.a;
    f_color = vec4(color, tex.a);
}
'''
