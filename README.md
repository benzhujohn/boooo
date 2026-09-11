# PORTFOLIO — 朱本

个人作品集网站。纯静态（HTML / CSS / 原生 JS），无构建步骤，直接部署在 GitHub Pages。

线上地址：**https://benzhujohn.github.io/boooo/**

---

## 五个板块

| # | 板块 | 说明 | 页面 |
|---|------|------|------|
| 01 | 网站建站 | WordPress / Oxygen / WooCommerce / SEO | `pages/web.html` |
| 02 | 平面设计 | Photoshop + Illustrator：说明书 / UI / 产品物料 / 标贴 / 易拉宝 | `pages/graphic.html` |
| 03 | AI 应用 | WorkBuddy / ComfyUI / Liblib | `pages/ai.html` |
| 04 | 3D 渲染 | Blender：建模 / 材质 / 灯光 / 渲染 | `pages/three-d.html` |
| 05 | 兴趣爱好 | 电脑 DIY / NAS DIY / 新工具 / 健身 / 规划 | `pages/life.html` |
| — | 项目经历与成果 | 履历、职责、产出与可量化结果 | `pages/experience.html` |

---

## 目录结构

```
.
├── index.html                # 首页（长滚动：Hero → 走马灯 → 关于 → 目录 → 五章 → 经历 → 页脚）
├── pages/
│   ├── web.html              # 01 网站建站
│   ├── graphic.html          # 02 平面设计
│   ├── ai.html               # 03 AI 应用
│   ├── three-d.html          # 04 3D 渲染
│   ├── life.html             # 05 兴趣爱好
│   └── experience.html       # 项目经历与成果
├── assets/
│   ├── css/style.css         # 全站设计系统（改这里就能改全站风格）
│   ├── js/main.js            # 交互：滚动显现 / 导航 / 悬停预览 / 筛选 / 数字动画
│   └── img/*.svg             # 占位图（替换成你的作品图即可）
└── tools/gen_placeholder.py  # 占位图生成脚本
```

---

## 怎么改成你自己的

### 1. 换占位图

把 `assets/img/` 里的 SVG 换成你的真实作品图，两种方式：

- **偷懒版**：同名覆盖。比如把 `web-01.jpg` 命名成 `web-01.svg` 是不行的——
  直接把 HTML 里的 `web-01.svg` 改成 `web-01.jpg`，再把图片丢进 `assets/img/` 即可。
- **推荐版**：图片统一放 `assets/img/`，在 HTML 里改 `src` 和 `alt`。

图片建议尺寸：

| 类名 | 比例 | 建议像素 |
|------|------|----------|
| `.tile--wide` | 16:10 | 1600 × 1000 |
| `.tile` / `.tile--square` | 1:1 | 1200 × 1200 |
| `.tile--tall` | 3:4 | 1200 × 1600 |

### 2. 改配色

全部在 `assets/css/style.css` 顶部的 `:root` 里：

```css
--paper: #F4F3EF;   /* 背景底色 */
--ink:   #0B0B0C;   /* 正文字色 */
--accent:#D8452A;   /* 主强调色 */

/* 五个章节各自的识别色，只在序号 / 下划线 / 标签等极小面积出现 */
--ch-web:     #1F3A5F;
--ch-graphic: #D8452A;
--ch-ai:      #6B4EE6;
--ch-d3:      #C0703A;
--ch-life:    #4A6B4F;
```

### 3. 改字体

同样在 `:root`。当前用 Google Fonts 异步加载
（Inter / Instrument Serif / IBM Plex Mono），
**加载失败会自动回退到系统字体**，不会卡住渲染。要换成自托管字体，
把字体文件丢进 `assets/fonts/`，改用 `@font-face` 即可。

### 4. 改文案中的占位内容

全站搜这几个关键词就能找全：

| 搜索 | 说明 |
|------|------|
| `朱本` | 姓名 |
| `hello@example.com` | 邮箱（出现多处，含导航菜单和页脚） |
| `公司名称占位` | 履历里的公司名 |
| `◯◯ 待填` | 需要补真实数据的结果指标 |
| `benzhujohn` | GitHub 链接 |

---

## 交互说明

- **悬停预览**：首页目录列表，鼠标移上去会有图片跟随光标预览（仅桌面端）
- **滚动显现**：所有 `.reveal` 元素进入视口时淡入上移，可用 `.reveal-d1` ~ `.reveal-d5` 控制错峰
- **导航**：滚动超过 40px 变毛玻璃，进入深色区块自动反色
- **作品筛选**：子页面顶部的胶囊按钮，靠 `data-filter` 和 `data-cat` 匹配
- **数字动画**：`data-count="80"` 会从 0 滚到 80
- 已适配 `prefers-reduced-motion`

---

## 本地预览

无构建步骤，任意静态服务器即可：

```bash
python -m http.server 8080
# 然后打开 http://localhost:8080
```

> 直接双击 `index.html` 也能看，但部分浏览器对 `file://` 的字体和脚本有限制，
> 建议还是起个本地服务器。

---

## 部署到 GitHub Pages

仓库 → **Settings** → **Pages** → Source 选 **Deploy from a branch** →
Branch 选 **main**、目录选 **/ (root)** → Save。

等 1 分钟左右，访问 https://benzhujohn.github.io/boooo/

---

## 占位图重新生成

```bash
python tools/gen_placeholder.py
```

会按五个章节的配色，重新生成一套主题化 SVG 占位图。
