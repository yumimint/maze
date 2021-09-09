from math import floor


def hsv2rgb(h, s, v):
    h -= floor(h)
    r, g, b = v, v, v
    if s > 0.0:
        h *= 6.0
        i = int(h)
        f = h - i
        if i == 0:
            b *= 1.0 - s
            g *= 1.0 - s * (1.0 - f)
        elif i == 1:
            b *= 1.0 - s
            r *= 1.0 - s * f
        elif i == 2:
            r *= 1.0 - s
            b *= 1.0 - s * (1.0 - f)
        elif i == 3:
            r *= 1.0 - s
            g *= 1.0 - s * f
        elif i == 4:
            g *= 1.0 - s
            r *= 1.0 - s * (1.0 - f)
        elif i == 5:
            g *= 1.0 - s
            b *= 1.0 - s * f
    return r, g, b
