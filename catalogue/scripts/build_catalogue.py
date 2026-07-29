#!/usr/bin/env python3
"""
Sykon ABS GmbH — A4 portrait catalogue engine.

    python catalogue/scripts/build_catalogue.py <config.json> <image_dir> <out_dir>

Builds two PDFs from one config:

    <name>-print.pdf     216 x 303mm, 3mm bleed, crop marks, full-resolution art
    <name>-digital.pdf   210 x 297mm, trimmed, downsampled art, for email

Same engine as the Sykon Properties listing builders — Python assembles an HTML
string with inline CSS, Chromium renders it through Playwright, fonts and images
are base64-inlined, every page is a fixed-height box with overflow hidden, and
the page size is declared in mm in BOTH the @page rule and the page.pdf() call.
Those constraints are not stylistic. Each one is load-bearing:

  * fixed height + overflow:hidden is what keeps one page to one page. A flex
    child with flex:1 instead of a fixed height reliably spills a phantom page.
  * images are base64-inlined because Chromium's file:// renderer resolves
    relative image paths unpredictably.
  * the page size is set twice because setting it once produces an A4 that is a
    millimetre out.

Any image named in the config but missing from disk renders as a labelled proof
plate rather than failing the build. That is deliberate: it lets a layout be
approved before the photography or the section drawings exist.
"""
import os
import sys
import json
import base64
import mimetypes

HERE = os.path.dirname(os.path.abspath(__file__))
CAT = os.path.dirname(HERE)
ROOT = os.path.dirname(CAT)
sys.path.insert(0, os.path.join(ROOT, "brand", "dist"))

import sykon_tokens as TK  # noqa: E402

FONT_DIR = os.path.join(ROOT, "brand", "assets", "fonts")
LOGO_DIR = os.path.join(ROOT, "brand", "assets", "logo")
PATTERN_DIR = os.path.join(ROOT, "brand", "assets", "pattern")

TRIM_W, TRIM_H = TK.PAGE_W_MM, TK.PAGE_H_MM
BLEED = TK.BLEED_MM
MARGIN = TK.MARGIN_MM


# ------------------------------------------------------------------ helpers

def b64(path):
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        return "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode())


def esc(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def para(s):
    return esc(s).replace("\n\n", "</p><p>").replace("\n", "<br/>")


def svg_inline(path, fill=None):
    """Inline an SVG so it inherits colour and never triggers a fetch."""
    with open(path) as f:
        s = f.read()
    s = s.replace('<?xml version="1.0" encoding="UTF-8"?>', "").strip()
    return s


def plate(label, extra=""):
    """Stand-in for artwork that does not exist yet."""
    return (
        '<div class="plate" style="%s"><span>%s<br/>not supplied</span></div>'
        % (extra, esc(label))
    )


def img(images, key, cls="", style="", label=None):
    """Render an image, or a labelled proof plate when it is missing."""
    path = images.get(key)
    if not path or not os.path.exists(path):
        return plate(label or key, style)
    return '<img class="%s" style="%s" src="%s" alt="%s"/>' % (
        cls,
        style,
        b64(path),
        esc(label or key),
    )


# --------------------------------------------------------------------- css

def build_css(bleed_mm, marks):
    page_w = TRIM_W + 2 * bleed_mm
    page_h = TRIM_H + 2 * bleed_mm
    fonts = ""
    for fn in ("HankenGrotesk-latin-var.woff2", "HankenGrotesk-latin-ext-var.woff2"):
        p = os.path.join(FONT_DIR, fn)
        if os.path.exists(p):
            fonts += (
                "@font-face{font-family:'Hanken Grotesk';src:url(%s) format('woff2');"
                "font-weight:100 900;font-style:normal;font-display:block}\n" % b64(p)
            )

    crop = ""
    if marks:
        crop = """
.mark{position:absolute;background:%(ink)s}
.mark.h{width:%(b)smm;height:.25mm}
.mark.v{width:.25mm;height:%(b)smm}
.m-tl-h{top:%(b)smm;left:0}          .m-tl-v{top:0;left:%(b)smm}
.m-tr-h{top:%(b)smm;right:0}         .m-tr-v{top:0;right:%(b)smm}
.m-bl-h{bottom:%(b)smm;left:0}       .m-bl-v{bottom:0;left:%(b)smm}
.m-br-h{bottom:%(b)smm;right:0}      .m-br-v{bottom:0;right:%(b)smm}
""" % {"ink": TK.INK, "b": bleed_mm}

    return """
%(fonts)s
@page{size:%(pw)smm %(ph)smm;margin:0}
*{margin:0;padding:0;box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
html,body{background:%(page)s}
body{font-family:'Hanken Grotesk','Helvetica Neue',Arial,sans-serif;
     font-feature-settings:"liga" 1,"kern" 1;color:%(ink)s;-webkit-font-smoothing:antialiased}

.page{position:relative;width:%(pw)smm;height:%(ph)smm;background:%(page)s;
      overflow:hidden;page-break-after:always}
.page:last-child{page-break-after:auto}
.trim{position:absolute;top:%(b)smm;left:%(b)smm;width:%(tw)smm;height:%(th)smm}
/* The content box is absolutely positioned with a fixed inset, so a flex
   column inside it is bounded by the page and cannot spill a phantom page. */
.pad{position:absolute;top:%(b2)smm;left:%(b2)smm;right:%(b2)smm;bottom:%(b2)smm;
     display:flex;flex-direction:column}
.grow{flex:1 1 auto;min-height:0}
%(crop)s

/* ---- running furniture ---------------------------------------------- */
.pfoot{flex:0 0 auto;display:flex;align-items:baseline;justify-content:space-between;
       padding-top:3mm;border-top:.18mm solid rgba(0,0,0,.16)}
.band-red .pfoot,.band-ink .pfoot{border-top-color:rgba(255,255,255,.28)}
.pfoot .n{font-size:8.4px;font-weight:500;color:%(red)s}
.band-red .pfoot .n,.band-ink .pfoot .n{color:%(warm)s}

/* ---- type scale ---------------------------------------------------- */
.display{font-weight:300;font-size:30px;line-height:1.24;letter-spacing:-.012em}
.h1{font-weight:500;font-size:23px;line-height:1.22;letter-spacing:-.008em}
.h2{font-weight:500;font-size:15.5px;line-height:1.3}
/* 12%% tint, not 17%%: red on the 17%% tint measures 4.28:1, just under AA
   for text this size. The 12%% tint gives 4.66:1. */
.eyebrow{display:inline-block;align-self:flex-start;border-radius:9999px;background:%(tint12)s;color:%(red)s;
         padding:4px 12px;font-size:8.5px;font-weight:500;letter-spacing:.10em;text-transform:uppercase}
.lbl{font-size:7.6px;font-weight:500;letter-spacing:.16em;text-transform:uppercase;color:%(red)s}
.body{font-size:9.4px;font-weight:400;line-height:1.585;color:%(ink)s}
.body p+p{margin-top:3mm}
.small{font-size:8px;font-weight:300;line-height:1.5;color:%(ink)s;opacity:.72}
.foot{font-size:7.2px;font-weight:400;letter-spacing:.04em;opacity:.68}

/* Display headlines close with a terminal period. Brand signature, not a typo. */

/* ---- rules and fills ------------------------------------------------ */
.rule{height:.4mm;background:%(red)s;width:14mm}
.hair{height:.18mm;background:%(ink)s;opacity:.16}
.band-red{background:%(red)s;color:%(warm)s}
.band-ink{background:%(ink)s;color:%(paper)s}
.band-cool{background:%(cool)s}

/* On a dark or red ground, light type is warm — never pure white.
   And red is a graphic fill only: it measures 2.77:1 on ink. */
.band-red .lbl,.band-ink .lbl{color:%(warm)s}
.band-red .body,.band-ink .body{color:inherit}

/* ---- lists ---------------------------------------------------------- */
/* Print marker is a hyphen with a hanging indent. The red circle-and-check
   is the digital marker and does not belong in a printed catalogue. */
ul.sy{list-style:none}
ul.sy li{position:relative;padding-left:4.4mm;margin-bottom:1.6mm}
.band-red ul.sy li{margin-bottom:6mm;break-inside:avoid}
ul.sy li:before{content:"–";position:absolute;left:0;color:%(red)s;font-weight:500}
/* red on red is invisible, and red on ink is 2.77:1 — the marker goes warm
   on both coloured grounds */
.band-red ul.sy li:before,.band-ink ul.sy li:before{color:%(warm)s}

/* ---- product spot --------------------------------------------------- */
.spot{position:relative;border-radius:50%%;background:%(tint12)s;overflow:hidden}
.spot img{position:absolute;top:-8%%;left:-8%%;width:116%%;height:116%%;object-fit:contain}

/* ---- proof plate ---------------------------------------------------- */
.plate{width:100%%;height:100%%;background:%(cool)s;display:flex;align-items:center;
       justify-content:center;box-shadow:inset 0 0 0 .3mm rgba(0,0,0,.14)}
.spot .plate span{font-size:5.6px;letter-spacing:.10em}
.plate span{font-size:7px;font-weight:500;letter-spacing:.18em;text-transform:uppercase;
            color:rgba(0,0,0,.42);text-align:center;line-height:1.9}

/* ---- spec table ----------------------------------------------------- */
table.spec{width:100%%;border-collapse:collapse}
table.spec th{text-align:left;font-size:7.4px;font-weight:500;letter-spacing:.14em;
              text-transform:uppercase;color:%(red)s;padding:0 0 1.6mm 0;
              border-bottom:.3mm solid %(red)s}
table.spec td{font-size:9px;font-weight:400;padding:1.9mm 0;
              border-bottom:.18mm solid rgba(0,0,0,.14)}
table.spec td.k{width:46%%;opacity:.72}
table.spec td.v{font-weight:500}
""" % {
        "fonts": fonts,
        "pw": page_w, "ph": page_h,
        "tw": TRIM_W, "th": TRIM_H,
        "b": bleed_mm, "b2": bleed_mm + MARGIN,
        "crop": crop,
        "page": TK.PAGE, "paper": TK.PAPER, "ink": TK.INK, "red": TK.RED, "warm": TK.PAPER_WARM,
        "cool": TK.PAPER_COOL, "tint17": TK.RED_TINT_17, "tint12": TK.RED_TINT_12,
    }


# ------------------------------------------------------------------ blocks

def marks_html(marks):
    if not marks:
        return ""
    out = ""
    for c in ("tl", "tr", "bl", "br"):
        out += '<div class="mark h m-%s-h"></div><div class="mark v m-%s-v"></div>' % (c, c)
    return out


def watermark_chevron(opacity=".10", width_mm=124, right_mm=-30, bottom_mm=-22):
    """One oversized chevron, bleeding off an edge. Never repeated, never centred."""
    p = os.path.join(PATTERN_DIR, "chevron-red.svg")
    if not os.path.exists(p):
        return ""
    return (
        '<div style="position:absolute;right:%smm;bottom:%smm;width:%smm;opacity:%s;'
        'pointer-events:none">%s</div>'
        % (right_mm, bottom_mm, width_mm, opacity,
           svg_inline(p).replace("<svg ", '<svg style="width:100%;height:auto;display:block" ', 1))
    )


def pfoot(ctx):
    """Running furniture. Also what stops a short page reading as unfinished."""
    if not ctx.get("folio"):
        return ""
    return (
        '<div class="pfoot"><div class="foot">%s</div><div class="n">%s</div></div>'
        % (esc(ctx.get("running", "Sykon Aluminium Building Systems")), ctx["folio"])
    )


def head(eyebrow, heading, rule=True, color=None, maxw="132mm"):
    """Page head. Returned wrapped, so it is ONE flex item in .pad — otherwise
    each part becomes its own item and the pill eyebrow stretches full width."""
    out = ""
    if eyebrow:
        out += '<div class="eyebrow">%s</div>' % esc(eyebrow)
    if heading:
        style = "margin-top:7mm;max-width:%s" % maxw
        if color:
            style += ";color:%s" % color
        out += '<div class="h1" style="%s">%s</div>' % (style, esc(heading))
    if rule:
        out += '<div class="rule" style="margin-top:6mm"></div>'
    return '<div style="flex:0 0 auto">%s</div>' % out


def logo(name, height_mm):
    p = os.path.join(LOGO_DIR, name + ".svg")
    if not os.path.exists(p):
        return ""
    return '<div style="height:%smm;line-height:0">%s</div>' % (
        height_mm,
        svg_inline(p).replace(
            "<svg ", '<svg height="%smm" style="height:%smm;width:auto;display:block" '
            % (height_mm, height_mm), 1),
    )


def blk_cover(b, images, ctx):
    wave = os.path.join(PATTERN_DIR, "masthead-wave.svg")
    wave_svg = ""
    if os.path.exists(wave):
        wave_svg = (
            '<div style="position:absolute;top:0;left:0;width:100%%;">%s</div>'
            % svg_inline(wave).replace(
                "<svg ", '<svg style="width:100%;height:auto;display:block" ', 1
            )
        )
    # Product renders sit on tinted discs, overlapping, and are allowed to break
    # out of the disc. Sizes and offsets stagger so the group reads as a cluster
    # rather than a row of three equal circles.
    spots = ""
    items = b.get("products", [])[:3]
    for i, it in enumerate(items):
        d = (34, 44, 38)[i % 3]
        right = (10, 44, 86)[i % 3]
        bottom = (2, 12, 0)[i % 3]
        spots += (
            '<div class="spot" style="position:absolute;right:%smm;bottom:%smm;'
            'width:%smm;height:%smm">%s</div>'
            % (right, bottom, d, d,
               img(images, it.get("image", ""),
                   style="width:100%;height:100%;object-fit:contain;display:block",
                   label=it.get("name", "product")))
        )
    return """
<div class="page">
  {marks}
  {wave}
  <div style="position:absolute;top:{lt}mm;left:{lm}mm;width:96mm">{logo}</div>
  <div style="position:absolute;top:{ht}mm;left:{lm}mm;right:{lm}mm">
    <div class="display">{headline}</div>
    <div class="body" style="margin-top:6mm;max-width:112mm;opacity:.8">{deck}</div>
    <div style="position:relative;height:62mm;margin-top:16mm">{spots}</div>
  </div>
  <div style="position:absolute;left:0;right:0;bottom:0;height:62mm">{strip}</div>
</div>
""".format(
        marks=marks_html(ctx["marks"]),
        wave=wave_svg,
        lt=ctx["bleed"] + 19, lm=ctx["bleed"] + MARGIN, ht=ctx["bleed"] + 84,
        logo=logo("horizontal-reversed", 17),
        headline=esc(b.get("headline", "")),
        deck=para(b.get("deck", "")),
        spots=spots,
        strip=img(images, b.get("strip", ""), cls="",
                  style="width:100%;height:100%;object-fit:cover;display:block",
                  label="extrusion strip"),
    )


def blk_intro(b, images, ctx):
    cols = b.get("columns", [])
    left = para(cols[0]) if cols else ""
    right = para(cols[1]) if len(cols) > 1 else ""
    return """
<div class="page">
  {marks}
  <div style="position:absolute;left:0;right:0;bottom:0;height:104mm">{image}</div>
  <div class="pad">
    {head}
    <div class="body" style="margin-top:8mm;font-weight:500;max-width:150mm">{lead}</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:{g}mm;margin-top:9mm">
      <div class="body"><p>{left}</p></div>
      <div class="body"><p>{right}</p></div>
    </div>
    <div class="grow"></div>
    <div style="height:96mm"></div>
    {foot}
  </div>
</div>
""".format(
        marks=marks_html(ctx["marks"]),
        head=head(b.get("eyebrow", ""), b.get("heading", ""), maxw="120mm"),
        lead=para(b.get("lead", "")),
        g=TK.GUTTER_MM, left=left, right=right,
        image=img(images, b.get("image", ""), cls="",
                  style="width:100%;height:100%;object-fit:cover;display:block",
                  label="section image"),
        foot="",
    )


def blk_pillars(b, images, ctx):
    cells = ""
    for it in b.get("items", []):
        cells += (
            '<div><div class="h2" style="color:%s">%s</div>'
            '<div class="body" style="margin-top:2.4mm">%s</div></div>'
            % (TK.RED, esc(it.get("title", "")), para(it.get("body", "")))
        )
    return """
<div class="page">
  {marks}
  <div class="pad">
    {head}
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:11mm {g}mm;margin-top:12mm;flex:0 0 auto;align-content:start">
      {cells}
    </div>
    <div class="grow"></div>
    {chev}
    {foot}
  </div>
</div>
""".format(
        marks=marks_html(ctx["marks"]),
        head=head(b.get("eyebrow", ""), b.get("heading", "")),
        g=TK.GUTTER_MM, cells=cells,
        chev=watermark_chevron(),
        foot=pfoot(ctx),
    )


def blk_families(b, images, ctx):
    cells = ""
    for it in b.get("items", []):
        cells += (
            '<div><div class="spot" style="width:100%%;padding-top:100%%;position:relative">'
            '<div style="position:absolute;inset:0">%s</div></div>'
            '<div class="h2" style="margin-top:4mm">%s</div>'
            '<div class="small" style="margin-top:1.6mm">%s</div></div>'
            % (
                img(images, it.get("image", ""),
                    style="width:100%;height:100%;object-fit:contain;display:block",
                    label=it.get("name", "system")),
                esc(it.get("name", "")),
                para(it.get("note", "")),
            )
        )
    return """
<div class="page">
  {marks}
  <div class="pad">
    {head}
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12mm {g}mm;margin-top:12mm;flex:0 0 auto;align-content:start">
      {cells}
    </div>
    <div class="grow"></div>
    {chev}
    {foot}
  </div>
</div>
""".format(
        marks=marks_html(ctx["marks"]),
        head=head(b.get("eyebrow", ""), b.get("heading", "")),
        g=TK.GUTTER_MM, cells=cells,
        chev=watermark_chevron(width_mm=110), foot=pfoot(ctx),
    )


def blk_system(b, images, ctx):
    rows = ""
    for s in b.get("specs", []):
        rows += '<tr><td class="k">%s</td><td class="v">%s</td></tr>' % (
            esc(s.get("label", "")),
            esc(s.get("value", "")),
        )
    perf = ""
    for s in b.get("performance", []):
        perf += '<tr><td class="k">%s</td><td class="v">%s</td></tr>' % (
            esc(s.get("label", "")),
            esc(s.get("value", "")),
        )
    return """
<div class="page">
  {marks}
  <div class="pad">
    <div class="eyebrow">{eyebrow}</div>
    <div class="h1" style="margin-top:7mm">{name}</div>
    <div class="body" style="margin-top:4mm;max-width:118mm">{intro}</div>
    <div style="display:grid;grid-template-columns:1.15fr 1fr;gap:{g}mm;margin-top:9mm">
      <div style="height:86mm">{drawing}</div>
      <div>
        <table class="spec"><tr><th colspan="2">{t1}</th></tr>{rows}</table>
        <table class="spec" style="margin-top:9mm"><tr><th colspan="2">{t2}</th></tr>{perf}</table>
      </div>
    </div>
    <div style="flex:1 1 auto;min-height:0;margin-top:10mm">{photo}</div>
    {foot}
  </div>
</div>
""".format(
        marks=marks_html(ctx["marks"]),
        eyebrow=esc(b.get("eyebrow", "System")),
        name=esc(b.get("name", "")),
        foot=pfoot(ctx),
        intro=para(b.get("intro", "")),
        g=TK.GUTTER_MM,
        drawing=img(images, b.get("drawing", ""),
                    style="width:100%;height:100%;object-fit:contain;display:block",
                    label="section drawing"),
        t1=esc(b.get("specs_title", "Profile")),
        t2=esc(b.get("performance_title", "Performance")),
        rows=rows, perf=perf,
        photo=img(images, b.get("photo", ""),
                  style="width:100%;height:100%;object-fit:cover;display:block",
                  label="application photo"),
    )


def blk_highlights(b, images, ctx):
    items = "".join("<li>%s</li>" % para(x) for x in b.get("items", []))
    chev = os.path.join(PATTERN_DIR, "chevron-ink.svg")
    chev_svg = ""
    if os.path.exists(chev):
        chev_svg = (
            '<div style="position:absolute;right:-26mm;bottom:-18mm;width:118mm;opacity:.13">%s</div>'
            % svg_inline(chev).replace("<svg ", '<svg style="width:100%;height:auto;display:block" ', 1)
        )
    return """
<div class="page band-red">
  {marks}
  {chev}
  <div class="pad">
    <div class="lbl">{eyebrow}</div>
    <div class="h1" style="margin-top:7mm;color:{warm};max-width:130mm">{heading}</div>
    <div style="height:.4mm;width:14mm;background:{warm};margin-top:6mm"></div>
    <ul class="sy body" style="margin-top:14mm;color:{warm};max-width:158mm;
        column-count:2;column-gap:{g}mm;font-size:12px;line-height:1.72">{items}</ul>
    <div class="grow"></div>
    {foot}
  </div>
</div>
""".format(
        marks=marks_html(ctx["marks"]), chev=chev_svg,
        eyebrow=esc(b.get("eyebrow", "")), heading=esc(b.get("heading", "")),
        warm=TK.PAPER_WARM, g=TK.GUTTER_MM, items=items, foot=pfoot(ctx),
    )


def blk_certifications(b, images, ctx):
    cells = ""
    for m in b.get("marks", []):
        cells += (
            '<div style="text-align:left"><div style="height:16mm">%s</div>'
            '<div class="small" style="margin-top:3mm">%s</div></div>'
            % (
                img(images, m.get("image", ""),
                    style="height:100%;width:auto;object-fit:contain;display:block",
                    label=m.get("name", "mark")),
                esc(m.get("name", "")),
            )
        )
    return """
<div class="page">
  {marks}
  <div class="pad">
    {head}
    <div class="body" style="margin-top:7mm;max-width:132mm">{body}</div>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:{g}mm;margin-top:14mm">
      {cells}
    </div>
    <div class="grow"></div>
    {chev}
    {foot}
  </div>
</div>
""".format(
        marks=marks_html(ctx["marks"]),
        head=head(b.get("eyebrow", ""), b.get("heading", ""), maxw="124mm"),
        body=para(b.get("body", "")), g=TK.GUTTER_MM, cells=cells,
        chev=watermark_chevron(), foot=pfoot(ctx),
    )


def blk_serve(b, images, ctx):
    cols = ""
    for grp in b.get("groups", []):
        lis = "".join("<li>%s</li>" % esc(x) for x in grp.get("items", []))
        cols += (
            '<div><div class="h2">%s</div><ul class="sy body" style="margin-top:3.4mm">%s</ul></div>'
            % (esc(grp.get("title", "")), lis)
        )
    return """
<div class="page">
  {marks}
  <div class="pad">
    {head}
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:11mm {g}mm;margin-top:13mm;flex:1 1 auto;min-height:0;align-content:start">
      {cols}
    </div>
    {chev}
    {foot}
  </div>
</div>
""".format(
        marks=marks_html(ctx["marks"]),
        head=head(b.get("eyebrow", ""), b.get("heading", ""), color=TK.RED, maxw="120mm"),
        g=TK.GUTTER_MM, cols=cols,
        chev=watermark_chevron(), foot=pfoot(ctx),
    )


def blk_back(b, images, ctx):
    c = b.get("contact", {})
    chev = os.path.join(PATTERN_DIR, "chevron-ink.svg")
    chev_svg = ""
    if os.path.exists(chev):
        chev_svg = (
            '<div style="position:absolute;right:-34mm;top:78mm;width:170mm">%s</div>'
            % svg_inline(chev).replace("<svg ", '<svg style="width:100%;height:auto;display:block" ', 1)
        )
    lines = ""
    for k in ("company", "address", "phone", "email", "web"):
        if c.get(k):
            lines += "<div>%s</div>" % esc(c[k])
    return """
<div class="page band-red">
  {marks}
  {chev}
  <div class="pad">
    <div style="width:96mm">{logo}</div>
    <div class="body foot" style="position:absolute;left:0;bottom:0;color:{warm};line-height:1.9">
      {lines}
    </div>
  </div>
</div>
""".format(
        marks=marks_html(ctx["marks"]), chev=chev_svg,
        logo=logo("horizontal-reversed", 17), warm=TK.PAPER_WARM, lines=lines,
    )


def blk_sheet(b, images, ctx):
    """The per-system product spec sheet.

    Reproduces intake/materials/07-references/SAMPLE__USE_THIS.pdf, whose layout
    was measured element by element. Vertical bands, in mm from the page top:

        masthead        0      - 64.94
        red rule        64.94  - 66.67
        overview        66.67  - 129.96
        spec tables     129.96 - 200.82
        typologies      200.82 - 259.65
        footer          266.97 - 283.98

    Type area runs 14.03mm to 195.97mm; the typology strip and segment cards
    both centre on x = 105.

    TWO DELIBERATE DEPARTURES FROM THE SAMPLE, both required:

    1. The typology strip is LARGER than the sample's. Anthony's review said the
       section "appears too small, and the figures do not clearly represent the
       exact typologies". Cells go from roughly 7mm to 17mm, and the icons are
       the real typology drawings rather than the sample's repeated placeholder.
    2. Nothing prints that the source .docx does not support. The sample carries
       spec and certification figures that appear nowhere in the system
       documents; those rows are dropped rather than reproduced.
    """
    ink, red, warm = TK.INK, TK.RED, TK.PAPER_WARM

    chips = ""
    for c in b.get("chips", [])[:4]:
        icon = c.get("icon", "")
        chips += (
            '<div class="chip"><div class="chip-i">%s</div>'
            '<div><div class="chip-a">%s</div><div class="chip-c">%s</div></div></div>'
            % (
                img(images, icon, style="width:100%;height:100%;object-fit:contain") if icon else "",
                esc(c.get("value", "")),
                esc(c.get("note", "")),
            )
        )

    def table(title, rows):
        if not rows:
            return ""
        tr = ""
        for i, r in enumerate(rows):
            icon = r.get("icon", "")
            tr += (
                '<tr class="%s"><td class="ic">%s</td><td class="k">%s</td><td class="v">%s</td></tr>'
                % (
                    "alt" if i % 2 == 0 else "",
                    img(images, icon, style="width:3.6mm;height:3.6mm;object-fit:contain") if icon else "",
                    esc(r.get("label", "")),
                    esc(r.get("value", "")),
                )
            )
        return ('<div class="col"><div class="h-sec">%s</div>'
                '<table class="sheet">%s</table></div>' % (esc(title), tr))

    # A symbol is attached only where one honestly depicts that option. Where no
    # match exists the cell carries its label alone — a mislabelled typology
    # symbol in a technical catalogue is worse than an absent one.
    typ = ""
    for t in b.get("typologies", [])[:8]:
        p = t.get("svg", "")
        art = (svg_inline(p).replace("<svg ", '<svg style="width:100%;height:100%;display:block" ', 1)
               if p and os.path.exists(p) else "")
        lbl = "<br/>".join(esc(x.strip()) for x in t.get("name", "").split("|"))
        typ += '<div class="typ"><div class="typ-a">%s</div><div class="typ-l">%s</div></div>' % (art, lbl)

    cards = ""
    for seg in b.get("segments", [])[:4]:
        note = seg.get("note", "")
        cards += ('<div class="card"><div class="card-t">%s</div>%s</div>'
                  % (esc(seg.get("title", "")),
                     '<div class="card-b">%s</div>' % esc(note) if note else ""))

    # The overview list is the document's own bullets, quoted, not paraphrased.
    ovlist = ""
    items = b.get("overview_list", [])
    if items:
        lt = b.get("overview_list_title", "")
        ovlist = ('<div class="sh-lt">%s</div>' % esc(lt) if lt else "") + \
                 '<ul class="sy body">%s</ul>' % "".join(
                     "<li>%s</li>" % esc(x) for x in items)

    name = b.get("system_name", "")
    name_html = ("%s<b>%s</b>" % tuple(esc(x) for x in name.split("|", 1))
                 if "|" in name else esc(name))

    css = """
<style>
.sh-mast{position:absolute;top:0;left:0;width:100%%;height:64.94mm;background:%(ink)s;overflow:hidden}
.sh-glow{position:absolute;left:50%%;top:20mm;width:76mm;height:76mm;margin-left:-38mm;border-radius:50%%;
         background:radial-gradient(closest-side,rgba(193,23,32,.32),rgba(193,23,32,0))}
.sh-rule{position:absolute;top:64.94mm;left:0;width:100%%;height:1.73mm;background:%(red)s}
.sh-logo{position:absolute;top:12.7mm;left:14.2mm;height:11.2mm;z-index:3}
.sh-name{position:absolute;top:28.4mm;left:14.2mm;font-size:44px;font-weight:500;line-height:1.05;
         letter-spacing:-.02em;color:%(warm)s;z-index:3}
/* Not `red`: on the ink masthead that measures 2.77:1, below even the
   large-text threshold. `red-on-dark` is the minimum lift clearing 3:1. */
.sh-name b{color:%(reddark)s;font-weight:500}
.sh-sub{position:absolute;top:47mm;left:14.2mm;font-size:12.5px;font-weight:300;
        color:%(warm)s;opacity:.78;letter-spacing:.005em;z-index:3}
.sh-chips{position:absolute;top:53.5mm;left:14.1mm;display:flex;gap:8mm;z-index:3}
.chip{display:flex;align-items:center;gap:2.2mm}
.chip-i{width:7.3mm;height:7.6mm;border-radius:1.6mm;background:%(red)s;flex:0 0 auto;padding:1.4mm}
.chip-a{font-size:8.6px;font-weight:700;color:%(warm)s;line-height:1.14}
.chip-c{font-size:6.2px;color:%(warm)s;opacity:.62;line-height:1.26;margin-top:.3mm}
.sh-hero{position:absolute;top:5mm;right:-3mm;width:72mm;z-index:2}
.h-sec{font-size:17px;font-weight:500;color:%(red)s;letter-spacing:-.006em;margin-bottom:4.4mm}
.sh-body{position:absolute;top:74mm;left:14.03mm;width:106mm}
.sh-body ul.sy{margin-top:4.4mm}
.sh-body ul.sy li{font-size:9.2px;line-height:1.5;margin-bottom:1.4mm}
.sh-lt{margin-top:5mm;font-size:9.2px;font-weight:500}
.sh-body .body{font-size:9.2px;line-height:1.62}
.sh-body .body p+p{margin-top:3.2mm}
.sh-hair{position:absolute;left:14.03mm;width:181.94mm;height:.18mm;background:rgba(0,0,0,.15)}
.sh-specs{position:absolute;top:136mm;left:14.03mm;width:181.94mm;display:flex;gap:12mm}
.sh-specs .col{flex:1;min-width:0}
table.sheet{width:100%%;border-collapse:collapse}
table.sheet td{padding:1.5mm 2mm;font-size:8.2px;vertical-align:middle;line-height:1.25}
table.sheet tr.alt td{background:rgba(0,0,0,.032)}
table.sheet td.ic{width:5.6mm;padding-right:0}
table.sheet td.k{opacity:.86}
table.sheet td.v{text-align:right;font-weight:700;white-space:nowrap}
.sh-typ{position:absolute;top:212mm;left:14.03mm;width:181.94mm}
.typ-row{display:grid;grid-template-columns:repeat(4,1fr);gap:2.4mm;margin-top:4.4mm}
.typ{display:flex;align-items:center;gap:2.4mm;background:rgba(0,0,0,.032);
     border-radius:2mm;padding:2.2mm 3mm;min-height:8mm}
.typ-a{width:8mm;height:8mm;flex:0 0 auto;overflow:hidden}
.typ-a:empty{display:none}
.typ-l{font-size:8px;font-weight:500;color:%(red)s;line-height:1.24}
.sh-seg{position:absolute;top:246mm;left:14.03mm;width:181.94mm}
.sh-cards{position:absolute;top:256mm;left:14.07mm;width:181.86mm;display:grid;
          grid-template-columns:repeat(4,1fr);gap:3.2mm}
.card{background:rgba(0,0,0,.032);border-radius:2.2mm;padding:3.8mm 3.6mm;
      display:flex;align-items:center;min-height:12mm}
.card-t{font-size:11.5px;font-weight:500;color:%(red)s;line-height:1.18}
.card-b{font-size:6.6px;opacity:.72;margin-top:1.4mm;line-height:1.3}
.sh-foot{position:absolute;top:277mm;left:14.03mm;width:181.94mm;display:flex;
         align-items:center;justify-content:space-between}
.sh-cert{display:flex;align-items:center;gap:3.2mm;background:rgba(0,0,0,.032);
         border-radius:2.2mm;padding:2.4mm 3.6mm}
.sh-cert-t{font-size:8.6px;font-weight:700;line-height:1.16}
.sh-cert-t i{color:%(red)s;font-style:normal}
.sh-marks{display:flex;align-items:center;gap:2.4mm}
.sh-contact{font-size:8.2px;opacity:.82}
</style>
""" % {"ink": ink, "red": red, "warm": warm, "reddark": TK.RED_ON_DARK}

    return """
<div class="page">
  {pm}{css}
  <div class="sh-mast"><div class="sh-glow"></div></div>
  <div class="sh-rule"></div>
  <div class="sh-logo">{logo}</div>
  <div class="sh-name">{name}</div>
  {sub}
  <div class="sh-chips">{chips}</div>
  <div class="sh-hero">{hero}</div>
  <div class="sh-body"><div class="h-sec">{ovt}</div>
    <div class="body"><p>{ov}</p></div>
    {ovlist}
  </div>
  <div class="sh-hair" style="top:129.96mm"></div>
  <div class="sh-specs">{t1}{t2}</div>
  <div class="sh-hair" style="top:207mm"></div>
  <div class="sh-typ"><div class="h-sec">{tyt}</div><div class="typ-row">{typ}</div></div>
  <div class="sh-seg"><div class="h-sec">{segt}</div></div>
  <div class="sh-cards">{cards}</div>
  <!-- The certification badge and its PIV / ift / A|U|F marks are gone: no .docx
       evidences them, and a certification mark is the one claim on this page
       that carries legal weight. -->
  <div class="sh-foot">
    <div class="sh-contact">{contact}</div>
  </div>
</div>
""".format(
        pm=marks_html(ctx["marks"]), css=css,
        logo=logo("horizontal-reversed", 11.2), name=name_html, chips=chips,
        hero=img(images, b.get("hero", ""), style="width:100%;height:auto;display:block",
                 label="product render"),
        sub=('<div class="sh-sub">%s</div>' % esc(b["system_subtitle"])
             if b.get("system_subtitle") else ""),
        ovt=esc(b.get("overview_title", "Product Overview")),
        ov=para(b.get("overview", "")),
        ovlist=ovlist,
        t1=table(b.get("specs_title", "Technical Specifications"), b.get("specs", [])),
        t2=table(b.get("performance_title", "Tested Performance"), b.get("performance", [])),
        tyt=esc(b.get("typologies_title", "System Options")), typ=typ, cards=cards,
        segt=esc(b.get("segments_title", "")),
        contact=esc(b.get("contact", "www.sykon.ae  |  info@sykon.ae")),
    )


BLOCKS = {
    "sheet": blk_sheet,
    "cover": blk_cover,
    "intro": blk_intro,
    "pillars": blk_pillars,
    "families": blk_families,
    "system": blk_system,
    "highlights": blk_highlights,
    "certifications": blk_certifications,
    "serve": blk_serve,
    "back": blk_back,
}


# ------------------------------------------------------------------- build

#: Blocks that carry running furniture. The cover and back cover do not — a
#: folio on a cover reads as a mistake.
FOLIO_BLOCKS = {"intro", "pillars", "families", "system", "highlights",
                "certifications", "serve"}


def build_html(cfg, images, bleed_mm, marks):
    running = cfg.get("running", "Sykon Aluminium Building Systems")
    pages = ""
    folio = 0
    for b in cfg["pages"]:
        kind = b.get("block")
        fn = BLOCKS.get(kind)
        if not fn:
            raise SystemExit("  error: unknown block %r (known: %s)"
                             % (kind, ", ".join(sorted(BLOCKS))))
        folio += 1
        ctx = {
            "bleed": bleed_mm,
            "marks": marks,
            "running": running,
            "folio": "%02d" % folio if kind in FOLIO_BLOCKS else None,
        }
        pages += fn(b, images, ctx)
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>%s</title>"
        "<style>%s</style></head><body>%s</body></html>"
        % (esc(cfg.get("title", "Sykon ABS")), build_css(bleed_mm, marks), pages)
    )


def chromium_executable():
    """Prefer a Chromium already on the machine over one Playwright wants to fetch.

    Playwright pins a browser build to its own version, so a pip upgrade can
    orphan a perfectly good browser that is already installed. Where
    PLAYWRIGHT_BROWSERS_PATH points at a managed install, use whatever build is
    actually there; fall back to Playwright's own resolution otherwise.
    """
    root = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if not root or not os.path.isdir(root):
        return None
    import glob

    for pat in ("chromium-*/chrome-linux/chrome",
                "chromium_headless_shell-*/chrome-linux/headless_shell"):
        hits = sorted(glob.glob(os.path.join(root, pat)))
        if hits:
            return hits[-1]
    return None


def render(html, pdf_path, bleed_mm):
    from playwright.sync_api import sync_playwright

    tmp = pdf_path + ".html"
    with open(tmp, "w") as f:
        f.write(html)
    w = TRIM_W + 2 * bleed_mm
    h = TRIM_H + 2 * bleed_mm
    exe = chromium_executable()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
        page = browser.new_page()
        page.goto("file://" + os.path.abspath(tmp))
        page.wait_for_timeout(400)
        page.pdf(
            path=pdf_path,
            width="%smm" % w,
            height="%smm" % h,
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()
    os.remove(tmp)


def resolve_images(cfg, image_dir):
    """Map every image key in the config to a path on disk, if it exists."""
    keys = set()

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ("image", "drawing", "photo", "strip", "hero", "icon") and isinstance(v, str) and v:
                    keys.add(v)
                elif k == "cert_marks" and isinstance(v, list):
                    keys.update(x for x in v if isinstance(x, str) and x)
                else:
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(cfg)
    out = {}
    for k in keys:
        p = k if os.path.isabs(k) else os.path.join(image_dir, k)
        out[k] = p
    return out


def main():
    if len(sys.argv) < 4:
        raise SystemExit(
            "usage: python catalogue/scripts/build_catalogue.py "
            "<config.json> <image_dir> <out_dir>"
        )
    cfg_path, image_dir, out_dir = sys.argv[1:4]
    cfg = json.load(open(cfg_path))
    os.makedirs(out_dir, exist_ok=True)
    images = resolve_images(cfg, image_dir)

    name = cfg.get("slug") or os.path.splitext(os.path.basename(cfg_path))[0]

    missing = sorted(k for k, p in images.items() if not os.path.exists(p))

    outputs = []
    for label, bleed_mm, marks in (("print", BLEED, True), ("digital", 0, False)):
        html = build_html(cfg, images, bleed_mm, marks)
        pdf = os.path.join(out_dir, "%s-%s.pdf" % (name, label))
        render(html, pdf, bleed_mm)
        outputs.append((label, pdf, bleed_mm))

    print("\n  Sykon ABS catalogue — %s" % cfg.get("title", name))
    print("  %d page(s), blocks: %s"
          % (len(cfg["pages"]), ", ".join(b.get("block", "?") for b in cfg["pages"])))
    for label, pdf, bleed_mm in outputs:
        size = os.path.getsize(pdf) / 1e6
        print("    %-8s %6.2f MB   %gx%gmm%s"
              % (label, size, TRIM_W + 2 * bleed_mm, TRIM_H + 2 * bleed_mm,
                 "  (3mm bleed, crop marks)" if bleed_mm else "  (trimmed)"))
    if missing:
        print("\n  %d image(s) not supplied, rendered as proof plates:" % len(missing))
        for m in missing:
            print("    - %s" % m)
    print("")


if __name__ == "__main__":
    main()
