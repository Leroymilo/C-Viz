#version 330

in vec2 uv;
in vec2 size;
in vec2 origin;
in float zoom;

out vec4 color;

void f(inout vec2 z) {
    z = z*z*z;
}

void main() {
    vec2 uv0 = pos - (size / (2 * zoom));
    vec2 z = uv0 + uv / zoom;
}