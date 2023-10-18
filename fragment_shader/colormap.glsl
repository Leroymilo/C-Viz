// Copyright(c) 2021 Björn Ottosson
//
// Permission is hereby granted, free of charge, to any person obtaining a copy of
// this softwareand associated documentation files(the "Software"), to deal in
// the Software without restriction, including without limitation the rights to
// use, copy, modify, merge, publish, distribute, sublicense, and /or sell copies
// of the Software, and to permit persons to whom the Software is furnished to do
// so, subject to the following conditions :
// The above copyright noticeand this permission notice shall be included in all
// copies or substantial portions of the Software.
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

vec3 pow3(vec3 v, float k)
{
	return vec3(pow(v.x, k), pow(v.y, k), pow(v.z, k));
}

float srgb_transfer_function(float a)
{
	return .0031308f >= a ? 12.92f * a : 1.055f * pow(a, .4166666666666667f) - .055f;
}

float srgb_transfer_function_inv(float a)
{
	return .04045f < a ? pow((a + .055f) / 1.055f, 2.4f) : a / 12.92f;
}

vec3 linear_srgb_to_oklab(vec3 rgb)
{
	return pow3(
		rgb * mat3(
			0.4122214708f, 0.5363325363f, 0.0514459929f,
			0.2119034982f, 0.6806995451f, 0.1073969566f,
			0.0883024619f, 0.2817188376f, 0.6299787005f
		), 1.f/3.f
	) * mat3(
		0.2104542553f, 0.7936177850f, 0.0040720468f,
		1.9779984951f, 2.4285922050f, 0.4505937099f,
		0.0259040371f, 0.7827717662f, 0.8086757660f
	);
}

vec3 oklab_to_linear_srgb(vec3 Lab)
{
	return pow3(
		Lab * mat3(
			1, +0.3963377774f, +0.2158037573f,
			1, -0.1055613458f, -0.0638541728f,
			1, -0.0894841775f, -1.2914855480f
		), 3.f
	) * mat3(
		+4.0767416621f, -3.3077115913f, +0.2309699292f,
		-1.2684380046f, +2.6097574011f, -0.3413193965f,
		-0.0041960863f, -0.7034186147f, +1.7076147010f
	);
}

// Finds the maximum saturation possible for a given hue that fits in sRGB
// Saturation here is defined as S = C/L
// a and b must be normalized so a^2 + b^2 == 1
float compute_max_saturation(vec2 ab)
{
	// Max saturation will be when one of r, g or b goes below zero.

	// Select different coefficients depending on which component goes below zero first
	float k0;
	vec4 KS;
	vec3 W;

	if (dot(ab, vec2(-1.88170328f, -0.80936493f)) > 1)
	{
		// Red component
		k0 = +1.19086277f;
		KS = vec4(+1.76576728f, +0.59662641f, +0.75515197f, +0.56771245f);
		W = vec3(+4.0767416621f, -3.3077115913f, +0.2309699292f);
	}
	else if (dot(ab, vec2(1.81444104f, -1.19445276f)) > 1)
	{
		// Green component
		k0 = +0.73956515f;
		KS = vec4(-0.45954404f, +0.08285427f, +0.12541070f, +0.14503204f);
		W = vec3(-1.2684380046f, +2.6097574011f, -0.3413193965f);
	}
	else
	{
		// Blue component
		k0 = +1.35733652f;
		KS = vec4(-0.00915799f, -1.15130210f, -0.50559606f, +0.00692167f);
		W = vec3(-0.0041960863f, -0.7034186147f, +1.7076147010f);
	}

	// Approximate max saturation using a polynomial:
	float S = k0 + dot(KS, vec4(ab.x, ab.y, ab.x*ab.x, ab.x*ab.y));

	// Do one step Halley's method to get closer
	// this gives an error less than 10e6, except for some blue hues where the dS/dh is close to infinite
	// this should be sufficient for most applications, otherwise do two/three steps 

	vec3 Klms = ab * mat3x2(
		+0.3963377774f, +0.2158037573f,
		-0.1055613458f, -0.0638541728f,
		-0.0894841775f, -1.2914855480f
	);

	{
		vec3 lms = pow3(vec3(1) + S * Klms, 3.f);

		vec3 lms_dS =  3 * Klms * lms  * lms;
		vec3 lms_dS2 = 6 * Klms * Klms * lms;

		float f  = dot(W, lms);
		float f1 = dot(W, lms_dS);
		float f2 = dot(W, lms_dS2);

		S = S - f * f1 / (f1 * f1 - 0.5 * f * f2);
	}

	return S;
}

// finds L_cusp and C_cusp for a given hue
// a and b must be normalized so a^2 + b^2 == 1
vec2 find_cusp(vec2 ab)
{
	// First, find the maximum saturation (saturation S = C/L)
	float S_cusp = compute_max_saturation(ab);

	// Convert to linear sRGB to find the first point where at least one of r,g or b >= 1:
	vec3 rgb_at_max = oklab_to_linear_srgb(vec3(1, S_cusp * ab));
	float L_cusp = pow(1.f / max(max(rgb_at_max.r, rgb_at_max.g), rgb_at_max.b), 1.f/3.f);
	float C_cusp = L_cusp * S_cusp;

	return vec2(L_cusp , C_cusp);
}

// Finds intersection of the line defined by 
// L = L0 * (1 - t) + t * L1;
// C = t * C1;
// a and b must be normalized so a^2 + b^2 == 1
float find_gamut_intersection(float L1, float C1, float L0, vec2 cusp)
{
	// Find the intersection for upper and lower half seprately
	float t;
	if (((L1 - L0) * cusp.y - (cusp.x - L0) * C1) <= 0.f)
	{
		// Lower half
		t = cusp.y * L0 / (C1 * cusp.x + cusp.y * (L0 - L1));
	}
	else
	{
		// Upper half
		t = cusp.y * (L0 - 1.f) / (C1 * (cusp.x - 1.f) + cusp.y * (L0 - L1));
	}

	return t;
}

float toe(float x)
{
	float k_1 = 0.206f;
	float k_2 = 0.03f;
	float k_3 = (1.f + k_1) / (1.f + k_2);
	return 0.5f * (k_3 * x - k_1 + sqrt((k_3 * x - k_1) * (k_3 * x - k_1) + 4 * k_2 * k_3 * x));
}

float toe_inv(float x)
{
	float k_1 = 0.206f;
	float k_2 = 0.03f;
	float k_3 = (1.f + k_1) / (1.f + k_2);
	return (x * x + k_1 * x) / (k_3 * (x + k_2));
}

vec2 to_ST(vec2 cusp)
{
	return vec2(cusp.y / cusp.x, cusp.y / (1 - cusp.x));
}

// Returns a smooth approximation of the location of the cusp
// This polynomial was created by an optimization process
// It has been designed so that S_mid < S_max and T_mid < T_max
vec2 get_ST_mid(vec2 ab)
{
	float S = 0.11516993f + 1.f / (
		+7.44778970f + 4.15901240f * ab.y
		+ ab.x * (-2.19557347f + 1.75198401f * ab.y
			+ ab.x * (-2.13704948f - 10.02301043f * ab.y
				+ ab.x * (-4.24894561f + 5.38770819f * ab.y + 4.69891013f * ab.x
					)))
		);

	float T = 0.11239642f + 1.f / (
		+1.61320320f - 0.68124379f * ab.y
		+ ab.x * (+0.40370612f + 0.90148123f * ab.y
			+ ab.x * (-0.27087943f + 0.61223990f * ab.y
				+ ab.x * (+0.00299215f - 0.45399568f * ab.y - 0.14661872f * ab.x
					)))
		);

	return vec2(S, T);
}

vec3 get_Cs(vec3 Lab)
{
	vec2 cusp = find_cusp(Lab.yz);

	float C_max = find_gamut_intersection(Lab.x, 1.f, Lab.x, cusp);
	vec2 ST_max = to_ST(cusp);

	float C_mid;
	{
		// Scale factor to compensate for the curved part of gamut shape:
		float k = C_max / min((Lab.x * ST_max.x), (1.f - Lab.x) * ST_max.y);

		vec2 ST_mid = get_ST_mid(Lab.yz);

		// Use a soft minimum function, instead of a sharp triangle shape to get a smooth value for chroma.
		float C_a = Lab.x * ST_mid.x;
		float C_b = (1.f - Lab.x) * ST_mid.y;
		C_mid = 0.9 * k * pow( pow(C_a, -4.f) + pow(C_b, -4.f), -0.25 );
	}

	float C_0;
	{
		// for C_0, the shape is independent of hue, so ST are constant. Values picked to roughly be the average values of ST.
		float C_a = Lab.x * 0.4f;
		float C_b = (1.f - Lab.x) * 0.8f;

		// Use a soft minimum function, instead of a sharp triangle shape to get a smooth value for chroma.
		C_0 = pow( pow(C_a, -2.f) + pow(C_b, -2.f), -0.5 );
	}

	return vec3(C_0, C_mid, C_max);
}

vec4 okhsl_to_srgba(vec3 hsl)
{
	float h = hsl.x;
	float s = hsl.y;
	float l = hsl.z;

	if (l == 1.f)
	{
		return vec4(1.f, 1.f, 1.f, 1.f);
	}

	else if (l == 0.f)
	{
		return vec4(0.f, 0.f, 0.f, 1.f);
	}

	vec3 Lab = vec3(toe_inv(hsl.z), cos(2.f * pi * h), sin(2.f * pi * h));

	vec3 cs = get_Cs(Lab);

	float mid = 0.8;
	float mid_inv = 1.25;

	float C, t, k_0, k_1, k_2;

	if (s < mid)
	{
		t = mid_inv * s;

		k_1 = mid * cs.x;
		k_2 = (1.f - k_1 / cs.y);

		C = t * k_1 / (1.f - k_2 * t);
	}
	else
	{
		t = (s - mid)/ (1 - mid);

		k_0 = cs.y;
		k_1 = (1.f - mid) * cs.y * cs.y * mid_inv * mid_inv / cs.x;
		k_2 = (1.f - (k_1) / (cs.z - cs.y));

		C = k_0 + t * k_1 / (1.f - k_2 * t);
	}

	vec3 rgb = oklab_to_linear_srgb(vec3(Lab.x, C * Lab.yz));
	return vec4(
		srgb_transfer_function(rgb.r),
		srgb_transfer_function(rgb.g),
		srgb_transfer_function(rgb.b),
		1
    );
}

vec3 srgb_to_okhsl(vec3 rgb)
{
	vec3 Lab = linear_srgb_to_oklab(vec3(
		srgb_transfer_function_inv(rgb.r),
		srgb_transfer_function_inv(rgb.g),
		srgb_transfer_function_inv(rgb.b)
    ));

	float C = length(Lab.yz);

	float h = 0.5 + 0.5 * atan(-Lab.z, -Lab.y) / pi;

	vec3 cs = get_Cs(vec3(Lab.x, Lab.yz / C));

	// Inverse of the interpolation in okhsl_to_srgb:

	float mid = 0.8;
	float mid_inv = 1.25;

	float s;
	if (C < cs.y)
	{
		float k_1 = mid * cs.x;
		float k_2 = (1.f - k_1 / cs.y);

		float t = C / (k_1 + k_2 * C);
		s = t * mid;
	}
	else
	{
		float k_0 = cs.y;
		float k_1 = (1.f - mid) * cs.y * cs.y * mid_inv * mid_inv / cs.x;
		float k_2 = (1.f - (k_1) / (cs.z - cs.y));

		float t = (C - k_0) / (k_1 + k_2 * (C - k_0));
		s = mid + (1.f - mid) * t;
	}

	return vec3(h, s, toe(Lab.x));
}


vec4 hsl_to_rgba(vec3 hsl) {
    float c = hsl.y * (1.f - abs(2*hsl.z - 1.f));
    float h1 = mod(hsl.x * 6.f, 6.f);
    float x = c * (1.f - abs(mod(h1, 2.f) - 1.f));
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

    return vec4((color + vec3(hsl.z - c/2.f)).rgb, 1.f);
    // r, g, b and a should be in [0, 1]
}
