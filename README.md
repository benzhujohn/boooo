# PORTFOLIO — benzhujohn

个人作品集网站。纯静态（HTML / CSS / 原生 JS），无构建步骤，直接部署在 GitHub Pages。

线上地址：**https://boooo.top/** （GitHub Pages 原始地址：https://benzhujohn.github.io/boooo/）

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

每个板块都可以挂**案例详解页**（做法、判断、结果），入口见下方「案例详解页」。

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
│   ├── experience.html       # 项目经历与成果
│   └── case/                 # 案例详解页
│       ├── _TEMPLATE.html    # 空白模板（复制它来新建案例，已设 noindex）
│       ├── wordpress-oxygen.html
│       └── campaign-plan.html
├── assets/
│   ├── css/style.css         # 全站设计系统（改这里就能改全站风格）
│   ├── js/main.js            # 交互：滚动显现 / 导航 / 悬停预览 / 筛选 / 视频灯箱 / 数字动画
│   ├── img/*.svg             # 占位图（替换成你的作品图即可）
│   └── video/                # 视频演示（.mp4）与配套封面（.jpg）
└── tools/
    ├── gen_placeholder.py    # 占位图生成脚本
    ├── gen_video.py          # 演示视频生成脚本
    └── check_refs.py         # 站内引用校验（本地资源 / 锚点 / 孤儿页）
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
| `benzhujohn` | 站点署名（姓名不出现真实姓名） |
| `YmVuemh1am9obkBmb3htYWlsLmNvbQ==` | 邮箱 base64（main.js 里 initMailGuard 解码，防爬虫抓取） |
| `13892981183` | 微信号（页脚，点击复制） |
| `公司名称占位` | 履历里的公司名 |
| `◯◯ 待填` | 需要补真实数据的结果指标 |
| `benzhujohn` | GitHub 链接 |
| `[案例标题]` | 案例页模板里的占位符（`[模块名]` / `[类型]` / `[一句话交代背景]` 等同理） |

---

## 视频案例（点击播放）

作品网格里任何一个格子都可以变成「视频条目」——封面照常显示，中间多一个播放按钮，
点击后弹出灯箱真实播放。

### 加一个视频条目

1. 把视频和封面丢进 `assets/video/`（建议 MP4 / H.264，**不要**用 GIF）
2. 复制下面这段，粘到任意 `.work` 该在的位置：

```html
<div class="work work--video ch-d3 reveal">
  <button class="tile tile--wide" type="button"
          data-video="../assets/video/你的视频.mp4"
          data-poster="../assets/video/你的封面.jpg"
          data-vtitle="灯箱里的标题"
          data-vsub="副标题 · 一行说明">
    <span class="tile__badge">视频</span>
    <span class="vdur">00:12</span>
    <span class="vplay" aria-hidden="true"><i></i></span>
    <img src="../assets/video/你的封面.jpg" alt="封面说明">
    <span class="tile__cap"><span>格子下方标题</span><span>关键词</span></span>
  </button>
  <div class="work__meta"><h3>作品标题</h3><p>用到的工具 · 环节</p></div>
</div>
```

- `data-video` / `data-poster` 按页面层级写相对路径（`pages/` 下的页面是 `../assets/...`）
- `data-vtitle` / `data-vsub` 不写也能跑，灯箱只显示画面
- `data-cat="官网 内容"` 加上就能参与顶部胶囊筛选，多个分类用空格分隔

### 要挂 YouTube / B 站等外链

把 `data-video` 换成 `data-embed`，值是**嵌入地址**（`/embed/xxx`，不是 `watch?v=`）：

```html
<button class="tile tile--wide" type="button"
        data-embed="https://www.youtube.com/embed/视频ID"
        data-poster="../assets/video/封面.jpg"
        data-vtitle="标题" data-vsub="说明">
```

### 封面裁切注意事项

封面在卡片里走 `object-fit: cover`，**会被裁掉边角**：

| 卡片比例 | 16:9 封面被裁掉 |
|----------|-----------------|
| 16:10 | 左右各约 5% |
| 1:1 | 左右各约 22% |

所以封面上的关键文字（标题、角标、水印）**一律左右居中**，否则换个卡片比例就看不见了。
`tools/gen_video.py` 里生成的视频 HUD 就是按这个规则做的。

### 键盘操作

灯箱打开后：`Esc` 关闭 · `←` `→` 上一条/下一条 · `空格` 播放暂停 · 点击遮罩关闭。
关闭后焦点会还回原来的按钮，页面滚动同步解锁，`prefers-reduced-motion` 下不做过渡动画。

---

## 案例详解页

「建站 / 策划」这类需要讲清楚过程和判断的作品，不适合塞在作品网格里，
单独开一个页面来写。结构是固定的：**封面 → 四格速览 → 左侧目录 + 右侧正文 → 上下页导航**。

### 新建一个案例

```bash
cp pages/case/_TEMPLATE.html pages/case/我的案例.html
```

然后照着 `_TEMPLATE.html` 里的注释填。每一块都有用法说明：

| 区块 | 类名 | 用途 |
|------|------|------|
| 封面 | `.phero` + `.crumb` | 面包屑、序号、标题、技术栈 chips |
| 速览 | `.cfacts` | 四格：角色 / 周期 / 交付 / 结果 |
| 正文骨架 | `.cbody` + `.ctoc` + `.cmain` | 左目录右正文，移动端目录折成横滑胶囊 |
| 章节 | `.cs-sec` | 一个 `.cs-sec` = 一节，`id` 对应目录锚点 |
| 步骤 | `.cs-steps` | 带编号的步骤列表 |
| 阶段流程 | `.cs-flow` | 横向阶段卡（自动塌陷空轨道） |
| 对比 | `.cs-cmp` | 两栏「改前 / 改后」对比 |
| 配图 | `.cs-figs` | 图组 |
| 结论 | `.cs-res` | 结果条目 |
| 上下页 | `.cnav` | 上一个 / 下一个案例 |

> `_TEMPLATE.html` 已设 `<meta name="robots" content="noindex, nofollow">`，
> 复制出来的新页面记得照着改成真实标题；模板本身不会被搜索引擎收录。

### 把入口挂上去

案例页不会自己出现在站内，需要手动画一个入口。三种现成的做法：

**① 作品网格里的箭头链接**（`pages/web.html` Case 01 就是这个）

```html
<a class="link-arrow" href="case/wordpress-oxygen.html">
  查看完整案例详解 <span aria-hidden="true">↗</span>
</a>
```

**② 板块末尾的索引列表**（`pages/graphic.html` 末尾就是这个，复用已有的 `.idx` 组件）

```html
<nav class="idx mt-m reveal" aria-label="深度案例列表">
  <a class="idx__row" href="case/我的案例.html" style="--row-accent:var(--ch-graphic)">
    <span class="idx__num">CASE 01</span>
    <span class="idx__name">案例标题 <small>Campaign</small></span>
    <span class="idx__tags">
      <span>关键词一</span><span>关键词二</span><span>关键词三</span>
    </span>
    <span class="idx__arrow" aria-hidden="true">→</span>
  </a>
</nav>
```

`--row-accent` 传章节色变量（`--ch-web` / `--ch-graphic` / `--ch-ai` / `--ch-d3` / `--ch-life`），
悬停时的强调色就跟着这个走。`<small>` 里是英文小标签，不写也行。

**③ 视频条目旁边**：把 `.link-arrow` 放进 `.work__meta` 里即可。

> 还没建好的案例，可以先在 HTML 里用注释留个槽位（`pages/three-d.html` 里就是这么做的）。
> `tools/check_refs.py` 会自动剥离注释，不会误报成失效链接。

### 校验有没有写错

```bash
python tools/check_refs.py
```

会检查全站本地资源路径、页内锚点是否存在，并列出没有入链的孤儿页面。

---

## 交互说明

- **悬停预览**：首页目录列表，鼠标移上去会有图片跟随光标预览（仅桌面端）
- **滚动显现**：所有 `.reveal` 元素进入视口时淡入上移，可用 `.reveal-d1` ~ `.reveal-d5` 控制错峰
- **导航**：滚动超过 40px 变毛玻璃，进入深色区块自动反色
- **作品筛选**：子页面顶部的胶囊按钮，靠 `data-filter` 和 `data-cat` 匹配
- **视频灯箱**：`data-video` / `data-embed` 触发，支持键盘操作与焦点归还
- **案例目录高亮**：`.ctoc` 里的锚点随滚动自动高亮当前章节，移动端折成横滑胶囊条
- **数字动画**：`data-count="80"` 会从 0 滚到 80
- 已适配 `prefers-reduced-motion`

> 章节色有个坑：`.phero__no`（大号序号水印）本身挂着 `.reveal`，
> 而 `.reveal.is-in { opacity: 1 }` 会把水印的透明度整个吃掉。
> 所以 CSS 里用 `.phero__no.reveal.is-in { opacity: .16 }` 更高特异度夺回来；
> 深色区块上还要再抬一次（`.band--ink .phero__no.reveal.is-in`），
> 并改用 `--ch-ink` 里专门调亮的深底版本章节色。
>
> 另一类优先级陷阱：`<a>` 上的**文本样式**（如 `text-transform: uppercase`）
> 会一路继承到 URL 文本里，`.vrow` 里的 `assets/video/*.mp4` 就被变成全大写了。

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

自定义域名走仓库根目录的 `CNAME` 文件（当前是 `boooo.top`）。
根目录还有 `.nojekyll`——**别删**，删了下划线开头的路径会被 Jekyll 吃掉。

---

## 占位图与演示视频重新生成

```bash
python tools/gen_placeholder.py   # 按五个章节配色重生成一套 SVG 占位图
python tools/gen_video.py         # 重生成 3 条演示视频 + 封面
python tools/gen_video.py web-scroll   # 只重生成其中一条（可选 d3-turntable / d3-lighting / web-scroll）
```

`gen_video.py` 不依赖 Blender——它用纯 Python（Pillow + imageio-ffmpeg 内置的 ffmpeg 二进制）
软件渲染出针孔相机、背面剔除、画家算法的 3D 画面，再逐帧编码成 H.264。
装了 `pip install pillow imageio-ffmpeg` 就能跑。
