# -*- coding: utf-8 -*-
"""
生成占位视频（可实际播放的 mp4），让「点击播放」的视频灯箱在替换真实素材前就能演示。

产物：
  assets/video/d3-turntable.mp4  + .jpg   产品转台动画（3D 板块）
  assets/video/d3-lighting.mp4   + .jpg   布光演示（3D 板块）
  assets/video/web-scroll.mp4    + .jpg   页面滚动演示（建站板块）

依赖：Pillow、imageio-ffmpeg（内置 ffmpeg 可执行文件）
用法：python tools/gen_video.py               # 全部生成
      python tools/gen_video.py web-scroll    # 只生成指定的一条
"""
import math
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:  # pragma: no cover
    FFMPEG = shutil.which("ffmpeg")

W, H = 1280, 720
FPS = 30
DUR = 6.0
FRAMES = int(FPS * DUR)
TAU = math.tau

INK = (11, 11, 12)
ACCENT_D3 = (192, 112, 58)      # --ch-d3
ACCENT_WEB = (128, 164, 214)    # --ch-web 提亮到深底上可见
BODY = (100, 96, 92)
DEVICE = (1.78, 1.56, 1.06)     # 方正造型：任意角度都有体量，360° 转起来不塌
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "assets", "video"))

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\consola.ttf",
    r"C:\Windows\Fonts\lucon.ttf",
    r"C:\Windows\Fonts\arial.ttf",
]


def load_font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ---------------------------------------------------------------- 向量与相机
def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def norm(v):
    l = math.sqrt(dot(v, v)) or 1.0
    return (v[0] / l, v[1] / l, v[2] / l)


def rot_y(v, a):
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c + v[2] * s, v[1], -v[0] * s + v[2] * c)


def rot_x(v, a):
    c, s = math.cos(a), math.sin(a)
    return (v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c)


class Cam:
    """极简针孔相机：位置 + 目标点 + 焦距（单位是像素）。"""

    def __init__(self, pos, target, focal):
        self.pos = pos
        self.f = norm(sub(target, pos))
        self.r = norm(cross(self.f, (0, 1, 0)))
        self.u = cross(self.r, self.f)
        self.focal = focal

    def project(self, v):
        d = sub(v, self.pos)
        z = max(0.05, dot(d, self.f))
        return (W * 0.5 + dot(d, self.r) * self.focal / z,
                H * 0.5 - dot(d, self.u) * self.focal / z,
                z)


# ---------------------------------------------------------------- 几何
def box(dim, center=(0, 0, 0)):
    w, h, d = dim[0] / 2, dim[1] / 2, dim[2] / 2
    cx, cy, cz = center
    v = [
        (cx - w, cy - h, cz - d), (cx + w, cy - h, cz - d),
        (cx + w, cy + h, cz - d), (cx - w, cy + h, cz - d),
        (cx - w, cy - h, cz + d), (cx + w, cy - h, cz + d),
        (cx + w, cy + h, cz + d), (cx - w, cy + h, cz + d),
    ]
    f = [(4, 5, 6, 7), (1, 0, 3, 2), (5, 1, 2, 6),
         (0, 4, 7, 3), (3, 7, 6, 2), (0, 1, 5, 4)]
    return v, f


def face_normal(world, f):
    a, b, c = (world[f[0]], world[f[1]], world[f[2]])
    return norm(cross(sub(b, a), sub(c, a)))


def face_center(world, f):
    return tuple(sum(world[k][i] for k in f) / 4.0 for i in range(3))


def visible_faces(world, faces, cam, light):
    """背面剔除 + 由远及近排序；返回 (idx, 受光量)。"""
    out = []
    for idx, f in enumerate(faces):
        n = face_normal(world, f)
        cen = face_center(world, f)
        if dot(n, norm(sub(cam.pos, cen))) <= 0.01:
            continue
        out.append((cen[2], idx, max(0.0, dot(n, light))))
    out.sort(key=lambda r: r[0])
    return [(r[1], r[2]) for r in out]


def inset_poly(pts, k):
    """把多边形各顶点朝重心收缩到 k 倍 —— 用来做倒角。"""
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return [(cx + (p[0] - cx) * k, cy + (p[1] - cy) * k) for p in pts]


def lerp(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def shade(color, k):
    """把颜色按亮度 k 混向背景色。"""
    k = max(0.0, min(1.45, k))
    return tuple(int(round(INK[i] + (color[i] - INK[i]) * k)) for i in range(3))


# ---------------------------------------------------------------- 画面骨架
def vignette(img):
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse([-W * 0.30, -H * 0.62, W * 1.30, H * 1.62], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(150))
    return Image.composite(img, Image.new("RGB", (W, H), (5, 5, 6)), mask)


def floor_grid(dr, cam, floor_y, t, span=15, rows=28, bright=26):
    """地面透视网格；横向线随时间向观察者推进。"""
    for i in range(-span, span + 1):
        p1 = cam.project((i * 1.05, floor_y, -28))
        p2 = cam.project((i * 1.05, floor_y, 10))
        dr.line([p1[:2], p2[:2]], fill=(bright, bright, bright), width=1)
    for j in range(rows):
        p = (j / float(rows) + t * 0.5) % 1.0
        z = 10 - (p ** 2.6) * 38
        a = int(bright * 0.5 + 30 * (1 - p))
        l = cam.project((-16, floor_y, z))
        r = cam.project((16, floor_y, z))
        dr.line([l[:2], r[:2]], fill=(a, a, a), width=1)


def brackets(dr, accent, m=48, L=30, w=2, alpha=190):
    c = accent + (alpha,)
    for (cx, cy, dx, dy) in ((m, m, 1, 1), (W - m, m, -1, 1),
                             (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        dr.line([(cx, cy), (cx + dx * L, cy)], fill=c, width=w)
        dr.line([(cx, cy), (cx, cy + dy * L)], fill=c, width=w)


def caption(dr, accent, text, f):
    """底部居中的说明。

    刻意居中：海报在卡片里会被 object-fit:cover 裁切
    （16:10 裁掉左右各约 5%，1:1 裁掉各约 22%），
    只有左右居中的内容在任何裁切比例下都完整可见。
    """
    tw = dr.textlength(text, font=f)
    cx = W * 0.5
    y = H - 58
    pad = 26
    dr.line([(cx - tw / 2 - pad - 88, y + 7), (cx - tw / 2 - pad, y + 7)],
            fill=(56, 56, 58), width=1)
    dr.line([(cx + tw / 2 + pad, y + 7), (cx + tw / 2 + pad + 88, y + 7)],
            fill=(56, 56, 58), width=1)
    for sx in (cx - tw / 2 - pad - 92, cx + tw / 2 + pad + 92):
        dr.rectangle([sx - 2, y + 5, sx + 2, y + 9], fill=accent)
    dr.text((cx - tw / 2, y), text, font=f, fill=(174, 172, 168))


# ---------------------------------------------------------------- 面细节
def face_details(dr, idx, poly, k):
    """给不同朝向的面各自加细节，保证每个角度都有东西可看。"""
    inner = inset_poly(poly, 0.955)

    if idx == 0:                                       # 正面：内嵌面板 + 指示灯
        panel = inset_poly(inner, 0.78)
        dr.polygon(panel, fill=shade(BODY, k * 0.58))
        dr.line(panel + [panel[0]], fill=shade(BODY, k * 1.5), width=1)
        for s in (0.72, 0.80, 0.88):
            dr.line([lerp(panel[0], panel[1], s), lerp(panel[3], panel[2], s)],
                    fill=shade(BODY, k * 0.32), width=2)
        led = lerp(lerp(panel[0], panel[1], 0.12), lerp(panel[3], panel[2], 0.12), 0.5)
        dr.ellipse([led[0] - 4, led[1] - 4, led[0] + 4, led[1] + 4],
                   fill=ACCENT_D3 + (240,))

    elif idx == 2:                                     # 右侧：散热槽
        for s in (0.20, 0.32, 0.44, 0.56):
            dr.line([lerp(inner[0], inner[1], s), lerp(inner[3], inner[2], s)],
                    fill=shade(BODY, k * 0.40), width=3)
        for s in (0.18, 0.82):
            p = lerp(inner[0], inner[3], s)
            dr.rectangle([p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2],
                         fill=shade(BODY, k * 0.28))

    elif idx == 4:                                     # 顶面：接缝 + 排气孔
        dr.line([lerp(inner[0], inner[1], 0.16), lerp(inner[3], inner[2], 0.16)],
                fill=shade(BODY, k * 0.42), width=2)
        c = lerp(lerp(inner[0], inner[1], 0.86), lerp(inner[3], inner[2], 0.86), 0.5)
        dr.ellipse([c[0] - 11, c[1] - 11, c[0] + 11, c[1] + 11],
                   outline=shade(BODY, k * 0.34), width=2)


# ---------------------------------------------------------------- 视频 1：转台
def render_turntable(frame_dir):
    dim = DEVICE
    cam = Cam((0.0, 1.95, 6.9), (0.0, -0.04, 0.0), 1500.0)
    floor_y = -dim[1] / 2
    verts, faces = box(dim)
    f_cap = load_font(19)

    for i in range(FRAMES):
        t = i / FRAMES
        ang = t * TAU
        tilt = math.radians(12) + math.sin(ang * 2) * math.radians(1.6)
        light = norm((math.cos(ang * 0.5) * 0.8 + 0.3, 1.25, 0.9))

        world = [rot_x(rot_y(v, ang), tilt) for v in verts]
        pts = [cam.project(v)[:2] for v in world]
        vis = visible_faces(world, faces, cam, light)

        img = Image.new("RGB", (W, H), INK)
        dr = ImageDraw.Draw(img, "RGBA")
        floor_grid(dr, cam, floor_y, t)

        ks = {idx: 0.24 + 0.80 * lam ** 0.85 for idx, lam in vis}
        for idx, lam in vis:
            poly = [pts[j] for j in faces[idx]]
            dr.polygon(poly, fill=shade(BODY, ks[idx] * 0.50))     # 倒角圈
            dr.polygon(inset_poly(poly, 0.955), fill=shade(BODY, ks[idx]))
        for idx, lam in vis:
            if idx in (0, 2, 4):
                face_details(dr, idx, [pts[j] for j in faces[idx]], ks[idx])
        for idx, lam in vis:                                       # 受光侧轮廓高光
            if lam < 0.5:
                continue
            ring = inset_poly([pts[j] for j in faces[idx]], 0.955)
            dr.line(ring + [ring[0]], fill=(238, 236, 232, int(30 + lam * 70)), width=1)
        for p in pts:
            dr.ellipse([p[0] - 2.2, p[1] - 2.2, p[0] + 2.2, p[1] + 2.2],
                       fill=ACCENT_D3 + (200,))

        # 转台底盘刻度
        for d in range(60):
            a = ang + d * TAU / 60
            long_tick = (d % 5 == 0)
            r1, r2 = (2.42 if long_tick else 2.54), 2.70
            p1 = cam.project((math.sin(a) * r1, floor_y, math.cos(a) * r1))
            p2 = cam.project((math.sin(a) * r2, floor_y, math.cos(a) * r2))
            dr.line([p1[:2], p2[:2]], fill=(200, 198, 194, 118 if long_tick else 42), width=1)

        # 倒影：镜像后压缩到 0.5，避免拖成一条长影
        contact_y = cam.project((0, floor_y, 0))[1]
        rip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rip)
        refl = []
        for v in world:
            sp = cam.project((v[0], 2 * floor_y - v[1], v[2]))
            refl.append((sp[0], contact_y + (sp[1] - contact_y) * 0.5))
        for f in faces:
            rd.polygon([refl[j] for j in f], fill=(126, 122, 118, 54))
        rip = rip.filter(ImageFilter.GaussianBlur(7))
        img = Image.alpha_composite(img.convert("RGBA"), rip).convert("RGB")

        img = vignette(img)
        dr = ImageDraw.Draw(img, "RGBA")
        dr.line([(0, contact_y), (W, contact_y)], fill=(74, 72, 70), width=1)
        brackets(dr, ACCENT_D3)
        caption(dr, ACCENT_D3,
                "TURNTABLE  ·  ROTATION  %03d°" % int(round(math.degrees(ang) % 360)),
                f_cap)
        img.save(os.path.join(frame_dir, "f%04d.png" % i))
    return "assets/video/d3-turntable.mp4"


# ---------------------------------------------------------------- 视频 2：布光
def render_lighting(frame_dir):
    dim = DEVICE
    cam = Cam((0.0, 1.95, 6.9), (0.0, -0.04, 0.0), 1500.0)
    floor_y = -dim[1] / 2
    verts, faces = box(dim)
    ang = math.radians(-34)
    tilt = math.radians(12)
    world = [rot_x(rot_y(v, ang), tilt) for v in verts]
    pts = [cam.project(v)[:2] for v in world]
    f_cap, f_small = load_font(19), load_font(16)

    for i in range(FRAMES):
        t = i / FRAMES
        la = t * TAU
        light_pos = (math.sin(la) * 2.75, 1.78 + math.cos(la * 2) * 0.34,
                     math.cos(la) * 2.75 + 0.62)
        light_dir = norm(light_pos)          # 由物体指向光源 —— 受光判定的正确方向
        vis = visible_faces(world, faces, cam, light_dir)

        img = Image.new("RGB", (W, H), INK)
        dr = ImageDraw.Draw(img, "RGBA")
        floor_grid(dr, cam, floor_y, t, bright=24)

        ks = {idx: 0.26 + 0.68 * lam ** 0.75 for idx, lam in vis}   # 抬高环境光
        for idx, lam in vis:
            poly = [pts[j] for j in faces[idx]]
            dr.polygon(poly, fill=shade(BODY, ks[idx] * 0.50))
            dr.polygon(inset_poly(poly, 0.955), fill=shade(BODY, ks[idx]))
        for idx, lam in vis:
            if idx in (0, 2, 4):
                face_details(dr, idx, [pts[j] for j in faces[idx]], ks[idx])

        # 地面光斑：只在光源位于相机这一侧时可见
        front = max(0.0, light_dir[2])
        gp = cam.project((light_pos[0] * 0.42, floor_y, light_pos[2] * 0.42))
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse(
            [gp[0] - 200, gp[1] - 50, gp[0] + 200, gp[1] + 50],
            fill=ACCENT_D3 + (int(30 + 76 * front),))
        glow = glow.filter(ImageFilter.GaussianBlur(36))
        img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
        dr = ImageDraw.Draw(img, "RGBA")

        # 光源本体 + 指向物体的虚线（光源绕到背面时改为角标提示）
        lp = cam.project(light_pos)
        if front > 0.02:
            tgt = cam.project((0, 0.2, 0))
            for s in range(0, 100, 7):
                dr.line([(lp[0] + (tgt[0] - lp[0]) * s / 100.0,
                          lp[1] + (tgt[1] - lp[1]) * s / 100.0),
                         (lp[0] + (tgt[0] - lp[0]) * (s + 3.5) / 100.0,
                          lp[1] + (tgt[1] - lp[1]) * (s + 3.5) / 100.0)],
                        fill=ACCENT_D3 + (int(30 + 60 * front),), width=1)
            for r in (9, 17, 27):
                dr.ellipse([lp[0] - r, lp[1] - r, lp[0] + r, lp[1] + r],
                           outline=ACCENT_D3 + (max(0, 190 - r * 6),), width=1)
            dr.ellipse([lp[0] - 4, lp[1] - 4, lp[0] + 4, lp[1] + 4],
                       fill=(255, 240, 220))
            dr.text((lp[0] + 34, lp[1] - 9), "KEY", font=f_small, fill=ACCENT_D3)
        else:
            dr.text((W * 0.5 - 62, 74), "KEY  ·  BEHIND", font=f_small,
                    fill=(150, 148, 144))

        # 右侧光强标尺（留在 16:10 裁切安全区内）
        bx = W - 118
        dr.line([(bx, H * 0.26), (bx, H * 0.74)], fill=(48, 48, 50), width=1)
        for k2 in range(11):
            yy = H * 0.74 - k2 * (H * 0.48 / 10)
            dr.line([(bx, yy), (bx + (13 if k2 % 5 == 0 else 7), yy)],
                    fill=(74, 74, 76), width=1)
        lvl = (math.cos(la) + 1) / 2
        yy = H * 0.74 - lvl * (H * 0.48)
        dr.line([(bx, yy), (bx + 28, yy)], fill=ACCENT_D3, width=2)
        dr.text((bx - 32, H * 0.76 + 8), "EV", font=f_small, fill=(124, 122, 118))

        img = vignette(img)
        dr = ImageDraw.Draw(img, "RGBA")
        brackets(dr, ACCENT_D3)
        caption(dr, ACCENT_D3, "KEY LIGHT  ·  360° SWEEP  ·  HDRI", f_cap)
        img.save(os.path.join(frame_dir, "f%04d.png" % i))
    return "assets/video/d3-lighting.mp4"


# ---------------------------------------------------------------- 视频 3：滚动
BLOCKS = [
    ("HERO", 208, (236, 234, 229), "hero"),
    ("INDEX / 05 CHAPTERS", 176, (216, 214, 208), "rows"),
    ("WORKS · GRID 3", 262, (228, 226, 220), "grid"),
    ("CASE STUDY", 236, (204, 202, 196), "rows"),
    ("QUOTE", 168, (242, 240, 235), "quote"),
    ("FOOTER / CONTACT", 214, (20, 20, 22), "footer"),
]


def render_web_scroll(frame_dir):
    f_cap, f_small, f_ui = load_font(19), load_font(16), load_font(15)
    page_h = sum(b[1] for b in BLOCKS)

    # 窗口居中占 22.5%~77.5%：即使海报被裁成 1:1 也不会切到窗口
    bx, by = int(W * 0.225), 62
    bw = int(W * 0.55)
    bh = H - 158
    view_top = by + 30
    view_h = bh - 30

    for i in range(FRAMES):
        t = i / FRAMES
        img = Image.new("RGB", (W, H), (15, 15, 17))
        dr = ImageDraw.Draw(img, "RGBA")

        for gxy in range(0, W, 64):
            dr.line([(gxy, 0), (gxy, H)], fill=(23, 23, 25), width=1)
        for gxy in range(0, H, 64):
            dr.line([(0, gxy), (W, gxy)], fill=(23, 23, 25), width=1)

        # 浏览器外壳
        dr.rectangle([bx, by, bx + bw, by + bh], fill=(244, 243, 239),
                     outline=(62, 62, 64), width=1)
        dr.rectangle([bx, by, bx + bw, by + 30], fill=(226, 224, 219))
        for k, c in enumerate(((214, 96, 84), (222, 176, 84), (128, 196, 138))):
            dr.ellipse([bx + 12 + k * 17, by + 11, bx + 20 + k * 17, by + 19], fill=c)
        dr.line([(bx + 78, by + 24), (bx + bw - 16, by + 24)], fill=(198, 196, 191), width=1)

        p = (1 - math.cos(t * TAU)) / 2
        offset = p * max(0, page_h - view_h)

        clip = img.crop((0, view_top, W, by + bh))
        cdr = ImageDraw.Draw(clip, "RGBA")
        y = -offset
        for name, hh, col, kind in BLOCKS:
            ty = y
            cdr.rectangle([bx + 1, ty, bx + bw - 1, ty + hh], fill=col)
            dark = sum(col) < 200
            cdr.text((bx + 26, ty + 16), name, font=f_ui,
                     fill=(238, 236, 232, 165) if dark else (58, 58, 60, 175))
            skel = (74, 74, 76) if dark else (176, 174, 168)

            if kind == "hero":
                cdr.rectangle([bx + 26, ty + 50, bx + 330, ty + 118], fill=(52, 52, 54))
                cdr.rectangle([bx + 26, ty + 130, bx + 220, ty + 148], fill=skel)
                cdr.rectangle([bx + 26, ty + 162, bx + 120, ty + 186], fill=(60, 60, 62))
            elif kind == "rows":
                for r in range(int((hh - 62) // 34)):
                    cdr.line([(bx + 26, ty + 54 + r * 34), (bx + bw - 26, ty + 54 + r * 34)],
                             fill=skel, width=4 if r % 2 else 7)
            elif kind == "grid":
                cw = (bw - 64) // 3
                for r in range(2):
                    for c in range(3):
                        rx = bx + 26 + c * (cw + 6)
                        ry = ty + 50 + r * 96
                        cdr.rectangle([rx, ry, rx + cw, ry + 78], fill=(194, 192, 186))
                        cdr.line([(rx, ry + 60), (rx + cw, ry + 60)],
                                 fill=(170, 168, 162), width=2)
            elif kind == "quote":
                cdr.rectangle([bx + 26, ty + 56, bx + 400, ty + 96], fill=(84, 84, 88))
                cdr.rectangle([bx + 26, ty + 108, bx + 300, ty + 140], fill=(150, 148, 142))
            elif kind == "footer":
                cdr.rectangle([bx + 26, ty + 62, bx + 360, ty + 140], fill=(72, 72, 74))
                cdr.rectangle([bx + 26, ty + 162, bx + 200, ty + 180], fill=(48, 48, 50))
            y += hh

        dr.line([(bx + 1, view_top), (bx + bw - 1, view_top)], fill=(206, 204, 199), width=1)
        img.paste(clip, (0, view_top))

        bar_h = max(44, view_h * view_h / max(1, page_h))
        bar_y = view_top + (view_h - bar_h) * p
        dr.rectangle([bx + bw - 8, view_top + 2, bx + bw - 3, by + bh - 2], fill=(230, 228, 223))
        dr.rectangle([bx + bw - 8, bar_y, bx + bw - 3, bar_y + bar_h], fill=(124, 122, 118))

        # 光标
        cx = bx + bw * (0.42 + 0.16 * math.sin(t * TAU * 1.4))
        cy = view_top + 60 + math.sin(t * TAU * 2.2) * 46
        dr.polygon([(cx, cy), (cx, cy + 20), (cx + 6, cy + 14), (cx + 12, cy + 22),
                    (cx + 16, cy + 19), (cx + 10, cy + 11), (cx + 18, cy + 10)],
                   fill=(250, 250, 248), outline=(40, 40, 42))

        pct = "%d%%" % int(round(p * 100))
        dr.text((bx + bw - dr.textlength(pct, font=f_small), by - 30), pct,
                font=f_small, fill=ACCENT_WEB)
        dr.text((bx, by - 28), "WORDPRESS  /  OXYGEN  —  LIVE PREVIEW",
                font=f_small, fill=(150, 148, 144))
        caption(dr, ACCENT_WEB, "RESPONSIVE  ·  SCROLL  DEMO", f_cap)
        img.save(os.path.join(frame_dir, "f%04d.png" % i))
    return "assets/video/web-scroll.mp4"


# ---------------------------------------------------------------- 编码
# 封面取帧：挑一个能看清物体形态、且文字不被裁切的角度
POSTER_IDX = {"d3-turntable": 12, "d3-lighting": 8, "web-scroll": 24}
JOBS = [
    ("d3-turntable", render_turntable),
    ("d3-lighting", render_lighting),
    ("web-scroll", render_web_scroll),
]


def encode(frame_dir, out_path, poster_path, poster_idx):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    subprocess.run([
        FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
        "-framerate", str(FPS), "-i", os.path.join(frame_dir, "f%04d.png"),
        "-c:v", "libx264", "-preset", "slow", "-crf", "30",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.0",
        "-movflags", "+faststart", out_path,
    ], check=True)
    Image.open(os.path.join(frame_dir, "f%04d.png" % poster_idx)).convert("RGB").save(
        poster_path, "JPEG", quality=82, optimize=True, progressive=True)
    return os.path.getsize(out_path), os.path.getsize(poster_path)


def main(only=None):
    if not FFMPEG:
        print("未找到 ffmpeg，请先 pip install imageio-ffmpeg")
        return 1
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="vidframes-")
    try:
        for name, fn in JOBS:
            if only and name not in only:
                continue
            fd = os.path.join(tmp, name)
            os.makedirs(fd, exist_ok=True)
            fn(fd)
            vs, ps = encode(fd, os.path.join(OUT, name + ".mp4"),
                            os.path.join(OUT, name + ".jpg"), POSTER_IDX[name])
            print("%-14s  mp4 %6.0f KB   poster %5.0f KB" % (name, vs / 1024, ps / 1024))
            shutil.rmtree(fd, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or None))
