# -*- coding: utf-8 -*-
"""
占位视觉素材生成器
生成主题化 SVG 占位图，供作品集各板块使用。
替换真实作品时，只需用同名 .jpg/.png 覆盖并在 HTML 里改扩展名即可。
"""
import os
import math
import random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "img")
os.makedirs(OUT, exist_ok=True)

INK = "#0B0B0C"
PAPER = "#F4F3EF"
PAPER2 = "#E7E5DF"

CHAPTERS = {
    "web":     {"accent": "#1F3A5F", "soft": "#DDE2E9"},
    "graphic": {"accent": "#D8452A", "soft": "#F0DFD9"},
    "ai":      {"accent": "#6B4EE6", "soft": "#E3DEF8"},
    "d3":      {"accent": "#C0703A", "soft": "#F0E4D8"},
    "life":    {"accent": "#4A6B4F", "soft": "#DDE5DD"},
}


def head(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice">'
    )


def grain(w, h, op=0.055):
    return (
        f'<filter id="g"><feTurbulence type="fractalNoise" baseFrequency="0.85" '
        f'numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter>'
        f'<rect width="{w}" height="{h}" filter="url(#g)" opacity="{op}"/>'
    )


def frame(w, h, accent, pad=18, op=0.5):
    """四角标记，画廊取景框质感"""
    s = 22
    p = pad
    st = f'stroke="{accent}" stroke-width="1.25" opacity="{op}" fill="none"'
    return (
        f'<path d="M{p} {p + s} V{p} H{p + s}" {st}/>'
        f'<path d="M{w - p - s} {p} H{w - p} V{p + s}" {st}/>'
        f'<path d="M{w - p} {h - p - s} V{h - p} H{w - p - s}" {st}/>'
        f'<path d="M{p + s} {h - p} H{p} V{h - p - s}" {st}/>'
    )


def trap(w, h, label, accent, soft):
    """底：白纸 + 一块构图性的色域，让每张图有各自的章节气质"""
    return (
        f'<rect width="{w}" height="{h}" fill="#FFFFFF"/>'
        f'<rect width="{w}" height="{h}" fill="{soft}" opacity="0.5"/>'
        f'<rect x="0" y="0" width="{w}" height="{h*0.42:.0f}" fill="{accent}" opacity="0.10"/>'
        f'<rect x="{w*0.72:.0f}" y="{h*0.58:.0f}" width="{w*0.34:.0f}" height="{h*0.5:.0f}" '
        f'fill="{accent}" opacity="0.16"/>'
    )


# ---------------- 各构图 ----------------

def c_grid(w, h, a, s):
    rnd = random.Random(hash((w, h, "grid")))
    out = []
    cols, rows = 4, 5
    cw, ch = w / cols, h / rows
    for r in range(rows):
        for c in range(cols):
            if rnd.random() < 0.42:
                continue
            x, y = c * cw + 10, r * ch + 10
            ww, hh = cw - 20, ch - 20
            fill = a if rnd.random() < 0.16 else INK
            op = 1 if fill == a else round(rnd.uniform(0.11, 0.30), 3)
            out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{ww:.0f}" height="{hh:.0f}" fill="{fill}" opacity="{op}"/>')
    return "".join(out)


def c_orb(w, h, a, s):
    cx, cy = w * 0.5, h * 0.52
    out = []
    for i in range(9, 0, -1):
        rr = (min(w, h) * 0.46) * (i / 9)
        op = 0.11 + (9 - i) * 0.018
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{rr:.0f}" fill="none" stroke="{INK}" stroke-width="1" opacity="{op}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{min(w,h)*0.20:.0f}" fill="{a}"/>')
    out.append(f'<line x1="0" y1="{cy}" x2="{w}" y2="{cy}" stroke="{INK}" stroke-width="1" opacity="0.14"/>')
    out.append(f'<line x1="{cx}" y1="0" x2="{cx}" y2="{h}" stroke="{INK}" stroke-width="1" opacity="0.14"/>')
    return "".join(out)


def c_lines(w, h, a, s):
    out = []
    n = 13
    for i in range(n):
        y = h * (i + 1) / (n + 1)
        wide = w * (0.34 + 0.5 * abs(math.sin(i * 1.1)))
        out.append(f'<rect x="{w*0.1:.0f}" y="{y:.0f}" width="{wide:.0f}" height="2" fill="{INK}" opacity="0.24"/>')
    y = h * 0.5
    out.append(f'<rect x="{w*0.1:.0f}" y="{y-4:.0f}" width="{w*0.62:.0f}" height="9" fill="{a}"/>')
    return "".join(out)


def c_doc(w, h, a, s):
    """说明书 / 手册"""
    m = w * 0.16
    out = [f'<rect x="{m}" y="{h*0.08:.0f}" width="{w-2*m:.0f}" height="{h*0.84:.0f}" fill="#fff" stroke="{INK}" stroke-width="1" opacity="0.9"/>']
    out.append(f'<rect x="{m}" y="{h*0.08:.0f}" width="{w-2*m:.0f}" height="{h*0.055:.0f}" fill="{a}"/>')
    y = h * 0.20
    out.append(f'<rect x="{m*1.35:.0f}" y="{y:.0f}" width="{(w-2*m)*0.55:.0f}" height="12" fill="{INK}" opacity="0.75"/>')
    y += 26
    for i in range(7):
        wid = (w - 2 * m) * (0.62 - 0.06 * (i % 3))
        out.append(f'<rect x="{m*1.35:.0f}" y="{y:.0f}" width="{wid:.0f}" height="4" fill="{INK}" opacity="0.26"/>')
        y += 13
    out.append(f'<rect x="{m*1.35:.0f}" y="{h*0.63:.0f}" width="{(w-2*m)*0.42:.0f}" height="{(w-2*m)*0.3:.0f}" fill="{INK}" opacity="0.07"/>')
    out.append(f'<circle cx="{w-m*1.6:.0f}" cy="{h*0.72:.0f}" r="{w*0.045:.0f}" fill="{a}" opacity="0.85"/>')
    return "".join(out)


def c_ui(w, h, a, s):
    """界面 / UI"""
    m = w * 0.09
    out = [f'<rect x="{m}" y="{h*0.12:.0f}" width="{w-2*m:.0f}" height="{h*0.76:.0f}" rx="10" fill="#fff" stroke="{INK}" stroke-width="1"/>']
    out.append(f'<rect x="{m}" y="{h*0.12:.0f}" width="{w-2*m:.0f}" height="{h*0.075:.0f}" rx="10" fill="{INK}" opacity="0.92"/>')
    for i in range(3):
        out.append(f'<circle cx="{m+20+i*14:.0f}" cy="{h*0.12+h*0.0375:.0f}" r="4" fill="{PAPER}" opacity="0.45"/>')
    bx, by = m * 1.5, h * 0.26
    bw = (w - 2 * m) * 0.26
    for i in range(4):
        out.append(f'<rect x="{bx:.0f}" y="{by + i*22:.0f}" width="{bw:.0f}" height="10" rx="5" fill="{INK}" opacity="{0.5 if i==1 else 0.14}"/>')
    out.append(f'<rect x="{w-m*1.5-(w-2*m)*0.55:.0f}" y="{by:.0f}" width="{(w-2*m)*0.55:.0f}" height="{h*0.16:.0f}" rx="8" fill="{a}" opacity="0.9"/>')
    yy = by + h * 0.24
    for i in range(3):
        out.append(f'<rect x="{bx:.0f}" y="{yy + i*30:.0f}" width="{(w-2*m)*0.8:.0f}" height="{h*0.055:.0f}" rx="8" fill="{INK}" opacity="0.11"/>')
    return "".join(out)


def c_label(w, h, a, s):
    """标贴 / 包装"""
    cx = w * 0.5
    bw, bh = w * 0.40, h * 0.62
    x, y = cx - bw / 2, h * 0.19
    out = [f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{bh:.0f}" rx="{bw*0.07:.0f}" fill="{a}"/>']
    out.append(f'<rect x="{x+bw*0.14:.0f}" y="{y+bh*0.10:.0f}" width="{bw*0.72:.0f}" height="{bh*0.80:.0f}" rx="6" fill="none" stroke="{PAPER}" stroke-width="1.2" opacity="0.75"/>')
    out.append(f'<rect x="{x+bw*0.24:.0f}" y="{y+bh*0.19:.0f}" width="{bw*0.52:.0f}" height="9" fill="{PAPER}" opacity="0.95"/>')
    for i in range(4):
        out.append(f'<rect x="{x+bw*0.24:.0f}" y="{y+bh*0.30 + i*14:.0f}" width="{bw*(0.52 - 0.08*(i%2)):.0f}" height="3" fill="{PAPER}" opacity="0.55"/>')
    out.append(f'<circle cx="{cx:.0f}" cy="{y+bh*0.70:.0f}" r="{bw*0.13:.0f}" fill="none" stroke="{PAPER}" stroke-width="1.2" opacity="0.8"/>')
    return "".join(out)


def c_banner(w, h, a, s):
    """易拉宝 / 展架"""
    bw, bh = w * 0.34, h * 0.80
    x, y = w * 0.5 - bw / 2, h * 0.10
    out = [f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{bh:.0f}" fill="#fff" stroke="{INK}" stroke-width="1" opacity="0.95"/>']
    out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{bh*0.42:.0f}" fill="{a}"/>')
    out.append(f'<rect x="{x+bw*0.12:.0f}" y="{y+bh*0.06:.0f}" width="{bw*0.5:.0f}" height="10" fill="{PAPER}" opacity="0.9"/>')
    out.append(f'<circle cx="{x+bw*0.5:.0f}" cy="{y+bh*0.30:.0f}" r="{bw*0.20:.0f}" fill="{PAPER}" opacity="0.22"/>')
    yy = y + bh * 0.50
    for i in range(6):
        out.append(f'<rect x="{x+bw*0.12:.0f}" y="{yy + i*16:.0f}" width="{bw*(0.62 - 0.07*(i%3)):.0f}" height="3.5" fill="{INK}" opacity="0.22"/>')
    out.append(f'<rect x="{x+bw*0.12:.0f}" y="{y+bh*0.83:.0f}" width="{bw*0.36:.0f}" height="12" fill="{a}"/>')
    out.append(f'<line x1="{w*0.5:.0f}" y1="{y+bh:.0f}" x2="{w*0.5:.0f}" y2="{h*0.985:.0f}" stroke="{INK}" stroke-width="1" opacity="0.3"/>')
    return "".join(out)


def c_cube(w, h, a, s):
    """3D 几何体"""
    cx, cy, r = w * 0.5, h * 0.52, min(w, h) * 0.26
    def iso(x, y, z):
        px = cx + (x - z) * 0.866 * r
        py = cy + ((x + z) * 0.5 - y) * r
        return px, py
    V = [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
    P = [iso(*v) for v in V]
    # 放大
    P = [(cx + (px - cx) * 1.5, cy + (py - cy) * 1.5) for px, py in P]
    E = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    out = []
    out.append(f'<polygon points="{P[4]} {P[5]} {P[6]} {P[7]}" fill="{a}" opacity="0.16"/>')
    out.append(f'<polygon points="{P[1]} {P[2]} {P[6]} {P[5]}" fill="{a}" opacity="0.34"/>')
    for i, j in E:
        x1, y1 = P[i]; x2, y2 = P[j]
        op = 0.85 if (i, j) in [(1,2),(2,3),(5,6),(6,7),(1,5),(2,6)] else 0.35
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{INK}" stroke-width="1.15" opacity="{op}"/>')
    for p in P:
        out.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2.2" fill="{a}"/>')
    return "".join(out)


def c_nodes(w, h, a, s):
    """AI 工作流节点图"""
    rnd = random.Random(7)
    pts = []
    for i in range(14):
        pts.append((rnd.uniform(w * 0.1, w * 0.9), rnd.uniform(h * 0.12, h * 0.88)))
    out = []
    for i, p in enumerate(pts):
        for q in pts[i + 1:]:
            d = math.hypot(p[0] - q[0], p[1] - q[1])
            if d < min(w, h) * 0.30:
                out.append(f'<line x1="{p[0]:.0f}" y1="{p[1]:.0f}" x2="{q[0]:.0f}" y2="{q[1]:.0f}" stroke="{INK}" stroke-width="0.9" opacity="0.24"/>')
    for i, p in enumerate(pts):
        r = 5 if i % 4 else 8
        fill = a if i % 4 == 0 else INK
        op = 1 if i % 4 == 0 else 0.62
        out.append(f'<circle cx="{p[0]:.0f}" cy="{p[1]:.0f}" r="{r}" fill="{fill}" opacity="{op}"/>')
    out.append(f'<rect x="{w*0.08:.0f}" y="{h*0.06:.0f}" width="{w*0.30:.0f}" height="{h*0.035:.0f}" fill="{INK}" opacity="0.13"/>')
    out.append(f'<rect x="{w*0.08:.0f}" y="{h*0.115:.0f}" width="{w*0.18:.0f}" height="{h*0.035:.0f}" fill="{a}" opacity="0.85"/>')
    return "".join(out)


def c_rack(w, h, a, s):
    """NAS / 机架"""
    m = w * 0.14
    out = []
    rows = 5
    yy = h * 0.14
    rh = (h * 0.72) / rows
    for i in range(rows):
        out.append(f'<rect x="{m:.0f}" y="{yy:.0f}" width="{w-2*m:.0f}" height="{rh-6:.0f}" rx="3" fill="#fff" stroke="{INK}" stroke-width="1" opacity="0.9"/>')
        out.append(f'<rect x="{m:.0f}" y="{yy:.0f}" width="{(w-2*m)*0.05:.0f}" height="{rh-6:.0f}" fill="{a}" opacity="{0.7 if i==1 else 0.28}"/>')
        for k in range(3):
            out.append(f'<rect x="{m + (w-2*m)*0.14 + k*(w-2*m)*0.22:.0f}" y="{yy + (rh-6)*0.32:.0f}" width="{(w-2*m)*0.17:.0f}" height="{(rh-6)*0.36:.0f}" rx="2" fill="{INK}" opacity="0.17"/>')
        out.append(f'<circle cx="{w-m-18:.0f}" cy="{yy+(rh-6)/2:.0f}" r="3" fill="{a}" opacity="{0.9 if i<3 else 0.3}"/>')
        yy += rh
    return "".join(out)


def c_pcb(w, h, a, s):
    """主机 / DIY 硬件"""
    m = w * 0.12
    out = [f'<rect x="{m:.0f}" y="{h*0.10:.0f}" width="{w-2*m:.0f}" height="{h*0.80:.0f}" rx="6" fill="#fff" stroke="{INK}" stroke-width="1"/>']
    out.append(f'<circle cx="{(w-2*m)*0.5+m:.0f}" cy="{h*0.30:.0f}" r="{min(w,h)*0.17:.0f}" fill="none" stroke="{a}" stroke-width="2" opacity="0.9"/>')
    out.append(f'<circle cx="{(w-2*m)*0.5+m:.0f}" cy="{h*0.30:.0f}" r="{min(w,h)*0.09:.0f}" fill="{a}" opacity="0.9"/>')
    for i in range(6):
        ang = i * math.pi / 3 + 0.4
        r1 = min(w, h) * 0.17
        x1 = (w - 2 * m) * 0.5 + m + math.cos(ang) * r1
        y1 = h * 0.30 + math.sin(ang) * r1
        out.append(f'<line x1="{(w-2*m)*0.5+m:.0f}" y1="{h*0.30:.0f}" x2="{x1:.0f}" y2="{y1:.0f}" stroke="{a}" stroke-width="1" opacity="0.45"/>')
    for i in range(3):
        out.append(f'<rect x="{m+22:.0f}" y="{h*0.60 + i*24:.0f}" width="{(w-2*m)*0.62:.0f}" height="{h*0.045:.0f}" rx="3" fill="{INK}" opacity="0.13"/>')
    yy = h * 0.60
    for i in range(8):
        out.append(f'<rect x="{w-m-(w-2*m)*0.20+ i*0:.0f}" y="{yy + i*11 - 0:.0f}" width="{(w-2*m)*0.18:.0f}" height="6" rx="2" fill="{INK}" opacity="0.20"/>')
    return "".join(out)


def c_type(w, h, a, s):
    """字体 / 版面构成"""
    out = []
    out.append(f'<text x="{w*0.5:.0f}" y="{h*0.62:.0f}" font-family="Georgia,serif" font-size="{h*0.46:.0f}" fill="{INK}" text-anchor="middle" opacity="0.94" letter-spacing="-0.03em">Aa</text>')
    out.append(f'<rect x="{w*0.10:.0f}" y="{h*0.72:.0f}" width="{w*0.80:.0f}" height="1.5" fill="{INK}" opacity="0.2"/>')
    for i in range(4):
        out.append(f'<rect x="{w*0.10 + i*(w*0.80)/4:.0f}" y="{h*0.755:.0f}" width="{(w*0.80)/4 - 14:.0f}" height="4" fill="{INK}" opacity="0.16"/>')
        out.append(f'<rect x="{w*0.10 + i*(w*0.80)/4:.0f}" y="{h*0.80:.0f}" width="{(w*0.80)/4 - 30:.0f}" height="4" fill="{INK}" opacity="0.10"/>')
    out.append(f'<circle cx="{w*0.83:.0f}" cy="{h*0.20:.0f}" r="{w*0.055:.0f}" fill="{a}"/>')
    return "".join(out)


COMPS = {
    "grid": c_grid, "orb": c_orb, "lines": c_lines, "doc": c_doc, "ui": c_ui,
    "label": c_label, "banner": c_banner, "cube": c_cube, "nodes": c_nodes,
    "rack": c_rack, "pcb": c_pcb, "type": c_type,
}

# 文件名 -> (章节, 构图, 宽, 高)
SPEC = [
    ("hero-web",       "web",     "grid",   1600, 1000),
    ("hero-graphic",   "graphic", "label",  1600, 1000),
    ("hero-ai",        "ai",      "nodes",  1600, 1000),
    ("hero-d3",        "d3",      "cube",   1600, 1000),
    ("hero-life",      "life",    "pcb",    1600, 1000),

    ("web-01", "web", "ui",     1200, 900),
    ("web-02", "web", "grid",   1200, 900),
    ("web-03", "web", "lines",  1200, 900),
    ("web-04", "web", "ui",     900, 1200),

    ("graphic-01", "graphic", "doc",    1200, 900),
    ("graphic-02", "graphic", "ui",     1200, 900),
    ("graphic-03", "graphic", "label",  900, 1200),
    ("graphic-04", "graphic", "banner", 900, 1200),
    ("graphic-05", "graphic", "type",   1200, 900),
    ("graphic-06", "graphic", "grid",   1200, 900),

    ("ai-01", "ai", "nodes", 1200, 900),
    ("ai-02", "ai", "ui",    1200, 900),
    ("ai-03", "ai", "grid",  1200, 900),
    ("ai-04", "ai", "orb",   900, 1200),

    ("d3-01", "d3", "cube",  1200, 900),
    ("d3-02", "d3", "orb",   1200, 900),
    ("d3-03", "d3", "cube",  900, 1200),
    ("d3-04", "d3", "lines", 1200, 900),

    ("life-01", "life", "pcb",  1200, 900),
    ("life-02", "life", "rack", 1200, 900),
    ("life-03", "life", "grid", 1200, 900),
    ("life-04", "life", "orb",  900, 1200),

    ("exp-01", "web",  "lines", 1200, 900),
    ("exp-02", "d3",   "grid",  1200, 900),
    ("exp-03", "ai",   "nodes", 1200, 900),
]

for name, chap, comp, w, h in SPEC:
    pal = CHAPTERS[chap]
    a, s = pal["accent"], pal["soft"]
    body = (
        head(w, h)
        + trap(w, h, name, a, s)
        + COMPS[comp](w, h, a, s)
        + frame(w, h, a)
        + grain(w, h)
        + "</svg>"
    )
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(body)

# favicon / og
with open(os.path.join(OUT, "og-cover.svg"), "w", encoding="utf-8") as f:
    w, h = 1200, 630
    f.write(
        head(w, h)
        + f'<rect width="{w}" height="{h}" fill="{INK}"/>'
        + f'<circle cx="{w*0.86:.0f}" cy="{h*0.22:.0f}" r="{h*0.30:.0f}" fill="#D8452A" opacity="0.9"/>'
        + f'<rect x="80" y="{h-190}" width="180" height="4" fill="#F4F3EF" opacity="0.9"/>'
        + f'<text x="80" y="{h-120}" font-family="Georgia,serif" font-size="76" fill="#F4F3EF" letter-spacing="-0.03em">PORTFOLIO</text>'
        + f'<text x="80" y="{h-66}" font-family="monospace" font-size="20" fill="#F4F3EF" opacity="0.55" letter-spacing="0.22em">WEB / GRAPHIC / AI / 3D / LIFE</text>'
        + grain(w, h, 0.05)
        + "</svg>"
    )

print("generated", len(SPEC) + 1, "files ->", os.path.abspath(OUT))
