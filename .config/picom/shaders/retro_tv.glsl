#version 330

// Retro CRT TV Shader for Picom
// Place this file in ~/.config/picom/shaders/ and reference it in picom.conf

uniform float opacity;
uniform bool invert_color;
uniform sampler2D tex;
uniform float time;

in vec2 texcoord;

// Shader parameters - adjust these for different effects
const float SCANLINE_INTENSITY = 0.15;
const float PHOSPHOR_GLOW = 0.8;
const float SCREEN_CURVATURE = 0.02;
const float CHROMATIC_ABERRATION = 0.001;
const float NOISE_INTENSITY = 0.03;
const float BRIGHTNESS = 1.1;
const float CONTRAST = 1.2;
const float SATURATION = 1.3;

// Generate pseudo-random noise
float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
}

// Apply barrel distortion for CRT curvature
vec2 curve(vec2 uv) {
    uv = uv * 2.0 - 1.0;
    vec2 offset = abs(uv.yx) / vec2(6.0, 4.0);
    uv = uv + uv * offset * offset;
    uv = uv * 0.5 + 0.5;
    return uv;
}

// Vignette effect
float vignette(vec2 uv) {
    uv *= 1.0 - uv.yx;
    float vig = uv.x * uv.y * 15.0;
    return pow(vig, 0.25);
}

// Convert RGB to HSV
vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

// Convert HSV to RGB
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    vec2 uv = texcoord;
    
    // Apply screen curvature
    vec2 curved_uv = curve(uv);
    
    // Check if we're outside the curved screen bounds
    if (curved_uv.x < 0.0 || curved_uv.x > 1.0 || curved_uv.y < 0.0 || curved_uv.y > 1.0) {
        gl_FragColor = vec4(0.0, 0.0, 0.0, opacity);
        return;
    }
    
    // Chromatic aberration effect
    vec2 texel = 1.0 / textureSize(tex, 0);
    float r = texture(tex, curved_uv + vec2(CHROMATIC_ABERRATION, 0.0) * texel).r;
    float g = texture(tex, curved_uv).g;
    float b = texture(tex, curved_uv - vec2(CHROMATIC_ABERRATION, 0.0) * texel).b;
    
    vec3 color = vec3(r, g, b);
    
    // Scanlines
    float scanline = sin(curved_uv.y * 800.0) * SCANLINE_INTENSITY;
    color *= 1.0 - scanline;
    
    // Phosphor glow effect
    vec3 phosphor = color * PHOSPHOR_GLOW;
    color = mix(color, phosphor, 0.5);
    
    // Add some TV noise
    float noise = random(curved_uv + fract(time * 0.001)) * NOISE_INTENSITY;
    color += noise;
    
    // Adjust brightness and contrast
    color = (color - 0.5) * CONTRAST + 0.5;
    color *= BRIGHTNESS;
    
    // Enhance saturation for that retro look
    vec3 hsv = rgb2hsv(color);
    hsv.y *= SATURATION;
    color = hsv2rgb(hsv);
    
    // Apply vignette
    color *= vignette(curved_uv);
    
    // Subtle color tinting (greenish CRT phosphor)
    color *= vec3(0.95, 1.0, 0.95);
    
    // Clamp values
    color = clamp(color, 0.0, 1.0);
    
    if (invert_color) {
        color = vec3(1.0) - color;
    }
    
    gl_FragColor = vec4(color, opacity);
}
