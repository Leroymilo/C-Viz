// plane to screen mapping setting
uniform vec2 origin;
uniform vec2 size;
uniform float scale;

// color mapping settings
uniform int style;
// style is a collection of flags giving how should f(z) be represented
// 2 first bits give colormap : 00 for HSL, 10 for okHSL
// 1 bit to toggle arg as hue, 1 bit to toggle modulus as luminosity
// 4 bits to toggle style lines
uniform vec4 K;
// 4 values giving the 4 scalers of style lines (space between lines)

in vec2 uvs;
out vec4 f_color;

// actual function to render:
complex f(complex z) {
    return FUNCTION;
}

float stepper(float x) {
    return 4*pow(x,3) - 6*pow(x,2) + 3*x;
}

vec4 enhance(complex z) {
    // Get enhanced lighness for each "part" of z
    // Re(z), Im(z)
    float mx = mod(z.x, K.x) / K.x;
    float x = stepper(stepper(mx));
    float my = mod(z.y, K.y) / K.y;
    float y = stepper(stepper(my));
    // |z|
    float logr = log(c_abs(z).x) * K.z;
    float r = ceil(logr) - logr;
    // arg(z)
    float mt = mod(c_arg(z).x, pi/K.w);
    float t = stepper(stepper(mt));

    return vec4(x, y, r, t);
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
        float v = uv2.x + uv2.y;
        f_color = vec4(0.4) + vec4(0.2) * (mod(v, 2.0));
        return;
    }

    // Computes lum multiplier for every style line
    vec4 l_mults = enhance(z);

    float theta = c_arg(z).x / (2*pi) + 0.5;
    float rho = c_abs(z).x; rho = clamp(rho / (rho + 1), 0f, 0.999999);
    // float l_ = clamp(l / (l + 1), 0f, 0.999999);
    // float l_ = 0.4 + 0.2 * enhance_mod(l) * enhance_arg(h);
    // float l_ = 0.4 + 0.2 * enhance_part(z.x) * enhance_part(z.y);
    // l = 1 can break the okhsl converter because of float errors
    // float h_ = h/(2*pi) + 0.5;

    float h = 0, s = 0, l = 1;

    // Enable arg as hue
    if ((style & 4) > 0) {
        h = theta;
        s = 0.8;
        l = 0.5;
    }

    // Enable mod as luminosity
    if ((style & 8) > 0) {
        l = rho;
    }

    // Enables style lines
    if ((style & 240) > 0) {
        float mult = 1;
        for(int i=0; i<4; i++) {
            if ((style & (1 << (4+i))) > 0) {
                mult *= l_mults[i];
            }
        }
        l = 0.6 * l + 0.4 * mult;
    }

    switch (style & 3) {
        case 0:
            // HSL colormap
            f_color = hsl_to_rgb(h, s, l);
            break;
        case 1:
            // okHSL colormap
            RGB color = okhsl_to_srgb(HSL(h, s, l));
            f_color = vec4(color.r, color.g, color.b, 1);
            break;
    }
}