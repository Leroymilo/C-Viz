// plane to screen mapping setting
uniform vec2 origin;
uniform vec2 size;
uniform float scale;

// color mapping settings
uniform int color_map;    // 0 for HSL, 1 for okHSL

in vec2 uvs;
out vec4 f_color;

// actual function to render:
complex f(complex z) {
    return FUNCTION;
}

// main shader processing
void main() {
    vec2 uv1 = uvs * size/2 / scale + origin;
    complex z = complex(uv1.x, uv1.y);

    z = f(z);

    float h = c_arg(z).x;
    float l = c_abs(z).x;
    float l_ = clamp(l / (l + 1), 0f, 0.999999);
    float h_ = h/(2*pi) + 0.5;

    switch (color_map) {
        case 0:
            f_color = hl_to_rgb(h_, l_);
            break;
        case 1:
            RGB color = okhsl_to_srgb(HSL(h_, 0.7, l_));
            f_color = vec4(color.r, color.g, color.b, 1);
            break;
    }
}