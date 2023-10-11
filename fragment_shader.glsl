#version 450 core

#define pi      3.14159265358979311599796346854418516
#define e       2.71828182845904523536028747135266250
#define log10e  0.43429448190325176115678118549112696
// #define complex vec2

uniform vec2 origin;
uniform vec2 size;
uniform float scale;
uniform float lum_coef;

uniform sampler2D tex;

in vec2 uvs;
out vec4 f_color;

struct complex {
    float x;
    float y;
};

// Complex functions
complex c_re(complex z) {
    return complex(z.x, 0);
}

complex c_im(complex z) {
    return complex(z.y, 0);
}

complex c_conj(complex z) {
    return complex(z.x, -z.y);
}

complex c_arg(complex z) {
    return complex(atan(z.y, z.x), 0);
}

complex c_abs(complex z) {
    return complex(length(vec2(z.x, z.y)), 0);
}

complex c_rect(float r, float t) {
    return complex(r * cos(t), r * sin(t));
}

complex c_add(complex z1, complex z2) {
    return complex(z1.x + z2.x, z1.y + z2.y);
}

complex c_sub(complex z1, complex z2) {
    return complex(z1.x - z2.x, z1.y - z2.y);
}

complex c_inv(complex z) {
    complex c_z = c_conj(z);
    float d = (z.x*z.x + z.y*z.y);
    return complex(c_z.x/d, c_z.y/d);
}

complex c_mult(complex z1, complex z2) {
    return complex(z1.x*z2.x - z1.y*z2.y, z1.x*z2.y + z1.y*z2.x);
}

complex c_div(complex z1, complex z2) {
    return c_mult(z1, c_inv(z2));
}

complex c_pow(complex z1, complex z2) {
    float t1 = c_arg(z1).x;
    return c_rect(c_abs(z1).x * exp(-z2.y*t1), z2.x*t1);
}

complex c_exp(complex z) {
    return c_rect(exp(z.x), z.y);
}

complex c_log(complex z) {
    return complex(log(c_abs(z).x), c_arg(z).x);
}

complex c_log10(complex z) {
    return c_mult(complex(log10e, 0), c_log(z));
}

complex c_sqrt(complex z) {
    return c_rect(sqrt(c_abs(z).x), c_arg(z).x/2);
}

complex c_sin(complex z) {
    return complex(sin(z.x) * cosh(z.y), cos(z.x) * sinh(z.y));
}

complex c_cos(complex z) {
    return complex(cos(z.x) * cosh(z.y), -sin(z.x) * sinh(z.y));
}

complex c_tan(complex z) {
    return c_div(c_sin(z), c_cos(z));
}

complex c_asin(complex z) {
    complex root = c_sqrt(c_sub(complex(1.0, 0.0), c_mult(z,z)));
    return c_mult(complex(0, -1), c_log(c_add(complex(-z.y, z.x), root)));
}

complex c_acos(complex z) {
    complex root = c_sqrt(c_sub(c_mult(z,z), complex(1, 0)));
    return c_mult(complex(0, -1), c_log(c_add(z, root)));
}

complex c_atan(complex z) {
    float d = z.x * z.x + z.y * z.y - 2 * z.y + 1;
    float x = 1 - z.x * z.x - z.y * z.y;
    return c_mult(complex(0, 0.5), c_log(complex(x/d, -2 * z.x / d)));
}

complex c_sinh(complex z) {
    return complex(sinh(z.x) * cos(z.y), cosh(z.x) * sin(z.y));
}

complex c_cosh(complex z) {
    return complex(cosh(z.x) * cos(z.y), sinh(z.x) * sin(z.y));
}

complex c_tanh(complex z) {
    return c_div(c_sinh(z), c_cosh(z));
}

complex c_asinh(complex z) {
    complex z2 = complex(z.x * z.x - z.y * z.y, 2 * z.x * z.y);
    return c_log(c_add(z, c_sqrt(complex(z2.x + 1, z2.y))));
}

complex c_acosh(complex z) {
    complex z2 = complex(z.x * z.x - z.y * z.y, 2 * z.x * z.y);
    return c_log(c_add(z, c_sqrt(complex(z2.x - 1, z2.y))));
}

complex c_atanh(complex z) {
    float d = z.x * z.x + z.y * z.y - 2 * z.x + 1;
    float x = 1 - z.x * z.x - z.y * z.y;
    return c_mult(complex(0.5, 0), c_log(complex(x/d, 2 * z.y / d)));
}


// actual function to render:
complex f(complex z) {
    // // f(z) = z²
    // return c_mult(z, z);

    // // f(z) = e^z
    // return c_exp(z);

    // f(z) = (z²-2)/z²
    complex z2 = c_mult(z, z);
    return c_div(c_add(z2, complex(-2, 0)), z2);
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

    return vec4((color + vec3(l - c/2)).rgb, 1);
    // r, g, b and a should be in [0, 1]
}

// main shader processing
void main() {
    // vec2 texuvs = vec2(-0.5, -0.5) + uvs * vec2(1, -1) / 2;
    // if (texture(tex, texuvs).rgb == vec3(1, 1, 1)) {
        // Rendering the function
        vec2 uv1 = uvs * size/2 / scale + origin;
        complex z = complex(uv1.x, uv1.y);

        z = f(z);

        float h = c_arg(z).x / (2*pi) + 0.5;
        float l = c_abs(z).x;
        // l = 1 - exp( -lum_coef * l);
        l = l / (l + 1);
        f_color = hl_to_rgb(h, l);
    // }
    // else {
    //     // Rendering GUI
    //     f_color = vec4(texture(tex, texuvs));
    // }
}