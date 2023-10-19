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
    float val = atan(z.y, z.x);
    val = val < 0 ? val + 2*pi : val;
    return complex(val, 0);
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
    float r1 = c_abs(z1).x;
    float t1 = c_arg(z1).x;
    float r3 = pow(r1, z2.x) * exp(-z2.y*t1);
    float t3 = z2.y * log(r1) + t1 * z2.x;
    return c_rect(r3, t3);
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
