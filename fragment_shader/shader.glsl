// plane to screen mapping setting
uniform vec2 origin;
uniform vec2 size;
uniform float scale;

// color mapping settings
uniform int color_map;    // 0 for HSL, 1 for okHSL
uniform int style;
// a collection of flags giving how should f(z) be represented

in vec2 uvs;
out vec4 f_color;

// actual function to render:
complex f(complex z) {
    return FUNCTION;
}

float enhance_part(float x) {
    float K = 1;
    float m = mod(x, K) / K;
    return 4*pow(m,3) - 6*pow(m,2) + 3*m;
}

float enhance_mod(float rho) {
    float K = 5;
    float log_rho = log(rho)*K;
    return ceil(log_rho) - log_rho;
}

float enhance_arg(float arg) {
    float K = 15;
    float m = mod(arg, pi/K);
    return 4*pow(m,3) - 6*pow(m,2) + 3*m;
}

// main shader processing
void main() {
    vec2 uv1 = uvs * size/2 / scale + origin;
    complex z = complex(uv1.x, uv1.y);

    z = f(z);

    if (isinf(z.x) && isinf(z.y)) {
        f_color = vec4(1);
        return;
    }

    if (isnan(z.x) || isnan(z.y)) {
        vec2 uv2 = floor(uvs * size / 20);
        f_color = vec4(0.4) + vec4(0.2) * (mod(uv2.x + uv2.y,2f));
        return;
    }

    float h = c_arg(z).x;
    float l = c_abs(z).x;
    // float l_ = clamp(l / (l + 1), 0f, 0.999999);
    float l_ = 0.4 + 0.2 * enhance_mod(l) * enhance_arg(h);
    // float l_ = 0.4 + 0.2 * enhance_part(z.x) * enhance_part(z.y);
    // l = 1 can break the okhsl converter because of float errors
    float h_ = h/(2*pi) + 0.5;

    switch (color_map) {
        case 0:
            f_color = hl_to_rgb(h_, l_);
            break;
        case 1:
            RGB color = okhsl_to_srgb(HSL(h_, 0.8, l_));
            f_color = vec4(color.r, color.g, color.b, 1);
            break;
    }
}