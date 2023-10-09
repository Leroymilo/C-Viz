#version 450

#define pi acos(-1)
#define complex vec2

in vec2 uv;
in vec2 size;
in vec2 origin;
in float zoom;
in float lum_coef;

out vec3 color_out;

vec3 hl_to_rgb(float h, float l) {
    float c = 1 - abs(2*l - 1);
    float h1 = mod(h*6, 6);
    float x = c * (1 - abs(mod(h1,2) - 1));
    int i = int(h1);

    vec3 color;

    switch (i) {
        case 0: color = vec3(c, x, 0);
        case 1: color = vec3(x, c, 0);
        case 2: color = vec3(0, c, x);
        case 3: color = vec3(0, x, c);
        case 4: color = vec3(x, 0, c);
        case 5: color = vec3(c, 0, x);
    }

    return color + vec3(l - c/2);
    // r, g and b should be in [0, 1]
}

// Complex functions
complex conj(complex z) {
    return complex(z.x, -z.y);
}

float arg(complex z) {
    return atan(z.y, z.x);
}
// complex modulus is z.length

complex mult(complex z1, complex z2) {
    return complex(z1.x*z2.x - z1.y*z2.y, z1.x*z2.y + z1.y*z2.x);
}

complex inv(complex z) {
    return conj(z) / (z.x*z.x + z.y*z.y);
}

complex div(complex z1, complex z2) {
    return mult(z1, inv(z2));
}

complex exp(complex z) {
    return complex(exp(z.x)*cos(z.y), exp(z.x)*sin(z.y));
}

// actual function to render:
complex f(complex z) {
    return mult(z, mult(z, z));
}

// main shader processing
void main() {
    vec2 uv0 = origin - (size / (2 * zoom));
    complex z = complex(uv0 + uv / zoom);

    f(z);

    float h = arg(z) / (2*pi) + 0.5;
    float l = 1 - exp(-lum_coef * z.length());

    color_out = hl_to_rgb(h, l);
}