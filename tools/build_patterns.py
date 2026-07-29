#!/usr/bin/env python3
"""
Sykon ABS GmbH — pattern asset generator.

    python tools/build_patterns.py

Writes brand/assets/pattern/.

The chevron cannot be traced from the brand master. It appears on six pages and
on every one of them it bleeds off the trim edge, so its apex is never visible —
that is the documented behaviour of the device, not an accident of the crops. It
is therefore DERIVED from the symbol's own construction constants, which is also
what makes it read as family:

    band thickness   t = 0.17903 x height   (the symbol's horizontal bar)
    arm angle        33.4 degrees            (the symbol's diagonal family)

Validated against the artwork on p17 on the things a cropped photograph can
actually settle: top bar 0.71 of the visible width (0.70 here) and lower-arm
foot at 0.39 (0.38 here). Arm slope photographs at 31.2 degrees on a wrinkled
wall with perspective; the flat construction value is 33.4.

Overall bounding-box aspect is deliberately NOT matched to the artwork. Every
measurable box in the book is a lower bound because the apex is cropped off the
trim, so 0.98 is what survives the crop, not the shape. This construction comes
out at 1.19.

The chevron is NOT a logo variant. It never stands in for the symbol in a lockup
or an avatar slot. See brand/docs for the usage rules.
"""
import os
import math
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "brand", "assets", "pattern")
TOKENS = json.load(open(os.path.join(ROOT, "brand", "tokens", "sykon.tokens.json")))

RED = TOKENS["color"]["red"]["value"]
INK = TOKENS["color"]["ink"]["value"]
PAPER_WARM = TOKENS["color"]["paper-warm"]["value"]
TINT29 = TOKENS["color"]["red-tint-29"]["value"]
TINT17 = TOKENS["color"]["red-tint-17"]["value"]

T = TOKENS["symbol"]["module"]["t"] * 100.0   # band thickness in a H=100 space
THETA = 33.4
TAN = math.tan(math.radians(THETA))


# Centreline of the chevron, in the H=100 space.
#
# On overall proportion the artwork cannot arbitrate: the apex is cropped by the
# trim in all six instances, so every measurable bounding box is a lower bound,
# not the shape. What the artwork DOES fix, and what this reproduces, is the
# relationship between the parts —
#
#   top bar          0.71 of the visible width      (0.70 here)
#   lower arm foot   0.39 of the visible width      (0.38 here)
#   band thickness   the symbol's bar, 0.17903 H
#   arm angle        the symbol's diagonal family, 33.4 deg
#
# Arm runs are therefore round numbers in the construction space (45 upper,
# 80 lower) rather than reverse-engineered from a cropped photograph.
BAR_LEN = 55.0
APEX_X = 100.0
LOWER_RUN = 80.0
DROP = LOWER_RUN * TAN

P0 = (0.0, T / 2)
P1 = (BAR_LEN, T / 2)
P2 = (APEX_X, T / 2 + (APEX_X - BAR_LEN) * TAN)
P3 = (APEX_X - DROP / TAN, P2[1] + DROP)

PTS = [P0, P1, P2, P3]

# Bounding box, allowing for the miter at the apex and the butt caps.
half = T / 2
miter = half / math.sin(math.radians((180 - 2 * THETA) / 2)) if THETA else half
MINX = min(p[0] for p in PTS) - half
MAXX = max(p[0] for p in PTS) + miter
MINY = min(p[1] for p in PTS) - half
MAXY = max(p[1] for p in PTS) + half
W = MAXX - MINX
H = MAXY - MINY

POLY = " ".join("%.4f,%.4f" % (x - MINX, y - MINY) for x, y in PTS)


def svg(body, title, w=W, h=H):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.4f %.4f" '
        'role="img" aria-label="%s">\n  <title>%s</title>\n%s</svg>\n'
        % (w, h, title, title, body)
    )


def chevron(stroke, width=T, opacity=None, dash=None):
    op = ' opacity="%s"' % opacity if opacity is not None else ""
    da = ' stroke-dasharray="%s"' % dash if dash else ""
    return (
        '  <polyline points="%s" fill="none" stroke="%s" stroke-width="%.4f" '
        'stroke-linejoin="miter" stroke-miterlimit="10" stroke-linecap="butt"%s%s/>\n'
        % (POLY, stroke, width, op, da)
    )


def main():
    os.makedirs(OUT, exist_ok=True)
    written = []

    def w(name, content):
        p = os.path.join(OUT, name)
        with open(p, "w") as fh:
            fh.write(content)
        written.append(p)

    # --- solid chevron, the three sanctioned fills ----------------------
    w("chevron-red.svg", svg(chevron(RED), "Sykon chevron"))
    w("chevron-ink.svg", svg(chevron(INK), "Sykon chevron"))
    w("chevron-light.svg", svg(chevron(PAPER_WARM), "Sykon chevron"))

    # --- hairline outline variant ---------------------------------------
    # Stroke weight in the book is ~0.1% of artwork width, i.e. sub-1pt.
    hair = W * 0.001 * 8
    w(
        "chevron-outline-red.svg",
        svg(
            '  <polyline points="%s" fill="none" stroke="%s" stroke-width="%.4f" '
            'stroke-linejoin="miter" stroke-miterlimit="10"/>\n' % (POLY, RED, hair),
            "Sykon chevron outline",
        ),
    )

    # --- echo stack -----------------------------------------------------
    # Two progressively fainter copies stepped up-left along the arrow axis at
    # ~4% of artwork width per step, plus a hairline. Measured from p12/p17.
    step = W * 0.04
    body = ""
    for i, fill in ((2, TINT17), (1, TINT29)):
        body += (
            '  <g transform="translate(%.4f %.4f)">\n' % (-step * i, -step * i * 0.55)
            + chevron(fill)
            + "  </g>\n"
        )
    body += chevron(RED)
    w("chevron-echo.svg", svg(body, "Sykon chevron with echo offsets"))

    # --- tessellated band ------------------------------------------------
    # Packaging only. White at 8% over the ground — solved from flat print
    # fields on the vehicle livery (alpha 0.077-0.082).
    tile = 64.0
    band = (
        '  <defs>\n'
        '    <pattern id="sy-chevron-band" width="%.2f" height="%.2f" '
        'patternUnits="userSpaceOnUse">\n'
        '      <path d="M0 %.2f L%.2f 0 L%.2f %.2f" fill="none" stroke="#FFFFFF" '
        'stroke-opacity="0.08" stroke-width="%.2f"/>\n'
        '      <path d="M0 %.2f L%.2f %.2f L%.2f %.2f" fill="none" stroke="#FFFFFF" '
        'stroke-opacity="0.08" stroke-width="%.2f"/>\n'
        "    </pattern>\n  </defs>\n"
        '  <rect width="100%%" height="100%%" fill="%s"/>\n'
        '  <rect width="100%%" height="100%%" fill="url(#sy-chevron-band)"/>\n'
        % (
            tile, tile,
            tile / 2, tile / 2, tile, tile / 2, tile * 0.10,
            tile, tile / 2, tile / 2, tile, tile, tile * 0.10,
            RED,
        )
    )
    w("chevron-band-red.svg", svg(band, "Sykon chevron band", 512, 256))

    # --- masthead wave ---------------------------------------------------
    # The editorial rule from pp.13-14: a red masthead field terminates in a
    # swept wave curve, never a straight edge, and a solid red circle sits off
    # the curve as punctuation. Traced from the p14 catalogue cover: the field
    # fills the top-left, its lower edge sweeps up to the right, and the circle
    # sits in the cleared space to the right of the sweep.
    #
    # Emitted at A4 width so the catalogue engine can drop it straight in.
    ww, wh = 210.0, 92.0
    wave = (
        '  <path d="M0 0 H%.2f V%.2f '
        "C%.2f %.2f %.2f %.2f %.2f %.2f "
        "C%.2f %.2f %.2f %.2f 0 %.2f Z\" fill=\"%s\"/>\n"
        '  <circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>\n'
        % (
            ww,
            # shallow at the right trim, holding high so a white bay opens
            # beneath it, then plunging left into the belly
            wh * 0.075,
            ww * 0.900, wh * 0.085, ww * 0.830, wh * 0.120, ww * 0.780, wh * 0.235,
            # long shallow belly running left, deepening to the left trim
            ww * 0.660, wh * 0.520, ww * 0.330, wh * 0.700, wh * 0.760,
            RED,
            # the punctuation circle, detached, sitting in the white bay under
            # the shoulder — never touching the field it was cut from
            ww * 0.888, wh * 0.300, wh * 0.135, RED,
        )
    )
    w("masthead-wave.svg", svg(wave, "Sykon masthead wave", ww, wh))

    return written


if __name__ == "__main__":
    for p in main():
        print("  wrote %s" % os.path.relpath(p, ROOT))
    print(
        "\n  chevron construction: t=%.3f  angle=%.1f deg  bbox %.2f x %.2f (aspect %.4f)"
        % (T, THETA, W, H, W / H)
    )
