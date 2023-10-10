#version 450 core

#define pi 3.1415926535897932384626433832795
// #define complex vec2

uniform vec2 origin;
uniform vec2 size;
uniform float scale;
uniform float lum_coef;

in vec2 uvs;
out vec4 f_color;

struct complex {
    float x;
    float y;
};

// Complex functions
complex conj(complex z) {
    return complex(z.x, -z.y);
}

float arg(complex z) {
    return atan(z.y, z.x);
}

float modulus(complex z) {
    return length(vec2(z.x, z.y));
}

complex plus(complex z1, complex z2) {
    return complex(z1.x + z2.x, z1.y + z2.y);
}

complex mult(complex z1, complex z2) {
    return complex(z1.x*z2.x - z1.y*z2.y, z1.x*z2.y + z1.y*z2.x);
}

complex inv(complex z) {
    complex c_z = conj(z);
    float d = (z.x*z.x + z.y*z.y);
    return complex(c_z.x/d, c_z.y/d);
}

complex div(complex z1, complex z2) {
    return mult(z1, inv(z2));
}

// complex exp(complex z) {
//     return complex(exp(z.x)*cos(z.y), exp(z.x)*sin(z.y));
// }

// actual function to render:
complex f(complex z) {
    complex z2 = mult(z, z);
    return div(plus(z2, complex(-2, 0)), z2);
}

vec4 hl_to_rgb(float h, float l) {
    float c = 1 - abs(2*l - 1);
    float h1 = mod(h*6, 6);
    float x = c * (1 - abs(mod(h1,2) - 1));
    int i = int(h1);

    vec3 color;

    switch (i) {
        case 0: color = vec3(c, x, 0); break;
        case 1: color = vec3(x, c, 0); break;
        case 2: color = vec3(0, c, x); break;
        case 3: color = vec3(0, x, c); break;
        case 4: color = vec3(x, 0, c); break;
        case 5: color = vec3(c, 0, x); break;
    }

    return vec4((color + vec3(l - c/2)).xyz, 1);
    // r, g, b and a should be in [0, 1]
}

// main shader processing
void main() {
    vec2 uv1 = ((2*uvs-1) * size/2 + origin) / scale;
    complex z = complex(uv1.x, uv1.y);

    z = f(z);

    float h = arg(z) / (2*pi) + 0.5;
    float l = 1 - exp( -lum_coef * modulus(z));

    f_color = hl_to_rgb(h, l);
}

// void main() {
//     vec2 sample_pos = vec2(uvs.x + sin(uvs.y * 10 + time * 0.01) * 0.1, uvs.y);
//     f_color = vec4(texture(tex, sample_pos).rg, texture(tex, sample_pos).b * 1.5, 1.0);
// }