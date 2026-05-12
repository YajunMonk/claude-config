---
name: wechat-layout-cloner
description: 公众号排版复刻器。当用户给一个微信公众号文章链接（mp.weixin.qq.com），希望"复刻排版""仿这个样式""做成模板""保存成模板""照着这个排版""复制这篇的版式""1:1 还原排版""扒这篇的样式"时使用。比 wechat-theme-extractor 更专业：不只提取主色/字号，而是做组件级复刻（强调框/步骤圆点/引用卡/装饰分割线/行内高亮等），产出可复用的独立 HTML 模板。用户说"排版复刻""仿公众号排版""把这篇公众号样式扒下来""生成公众号模板""照这篇做个模板"等场景务必触发此 skill。
---

# 公众号排版复刻器（wechat-layout-cloner）

这个 skill 帮用户把任意一篇微信公众号文章的**整套排版语言**复刻成一份自包含 HTML 模板，之后写新文章时套进去直接渲染、复制到公众号编辑器即可。

和旧的 `wechat-theme-extractor` 的区别是：旧版只做"主题色/字号/行高"的粗粒度主题提取；本 skill 做**组件级完整复刻**——把原文里的自定义组件（强调框、步骤序号、引用卡、装饰分割线、行内高亮、图注等）都识别出来，保留成可复用的 class，产出一份能直接拿来排版新稿的"视觉品牌指南 + 排版引擎"。

---

## 为什么这样设计

公众号文章的视觉辨识度**不是**来自字号或行高本身，而是来自三个东西：

1. **调色板**——不是一个主色，而是一整套颜色关系（主色、辅色、正文色、次要文字色、几种背景色、强调色）
2. **组件**——像"左边竖线＋浅底色的强调框"、"陶土色圆形数字"、"`· · ·` 居中分割线"、"两端破折号的小标题"这些反复出现的图形单元
3. **节奏**——段落间距、标题间距、图片和文字的距离、首段有没有下沉字……这些决定了"这篇读起来像谁"

如果只提取颜色和字号（旧 skill 做的事），复刻出来的东西永远是"有点像又完全不像"。所以本 skill 的重点是：**识别并命名这些组件**，把它们作为可复用的 class 写进模板里。

---

## 工作流

### 方式一：复刻新模板（从公众号文章提取）

1. 用户给一个微信文章 URL
2. 运行 `scripts/fetch.py <url>`——拉 HTML、提取 `#js_content`、提取 `<style>` 标签、保存元信息（标题/作者/发布时间）到 `workspace/{slug}/`
3. 你（AI）读取抓到的内容，对照 `references/component-patterns.md` 的组件图鉴逐项识别
4. 按 `references/extraction-guide.md` 的清单系统性填写一份"排版规格"
5. 基于 `templates/_skeleton.html` 骨架，用提取的规格生成一份 `templates/{style-name}.html`——AI 起一个有辨识度的文件名（比如 `warm-orange-magazine.html`、`minimal-mono-grid.html`、`serif-editorial-black.html`）
6. 在生成的模板里放一段完整的 **demo 正文**，覆盖所有识别出来的组件（标题 1/2/3、正文、引用、列表、强调框、分割线、图片+图注、代码、行内高亮），用户在浏览器里打开就能直观看到每个组件的样子
7. 在模板右上角放一个"全选正文"按钮和一段使用说明
8. 输出一份简短的 **复刻报告** 给用户：这套排版的设计语言是什么、有哪些组件、每个组件的语义用途建议

### 方式二：使用实时编辑器（推荐）

打开 `editor.html` 使用可视化编辑器：

1. **左侧编辑区**：输入 Markdown 原文
2. **右侧预览区**：实时显示排版效果
3. **右上角选择器**：切换不同的克隆风格模板
4. **一键复制**：点击"复制排版内容"按钮，直接粘贴到公众号编辑器

**优势**：
- 所见即所得，实时预览排版效果
- 可以快速对比不同风格
- 支持 Markdown 语法，写作更高效
- 一键复制，无需手动选择内容

---

## 规格表（你要填的东西）

系统地过一遍以下这张表，不要凭感觉"大概提取一下"。把每一项都明确写到模板的 CSS 里。遇到拿不准的字段，**宁可明写"原文没有，默认 X"**，也不要让它从模板里消失——因为下次用模板写新文章时，这些字段会被真实触发。

### ⚠️ 全局背景色（首先处理，不能漏）

**这是对最终视觉效果影响最大的单个字段，也是最容易"看着对、复制过去就丢"的坑。**

公众号文章的背景色通常设在最外层 `<section>` 上，而不是 `<body>`。因为只出现一次，频次统计里看不到它，极容易被遗漏——但它决定了整篇文章的底色气质。

#### 提取
1. 读 `summary.json` 的 `IMPORTANT_page_background` 字段（`fetch.py` 已经专门提取过外层 section 背景）
2. 把这个值赋给 `--color-bg-page`，同时把它放到 `body { background-color: ... }`，方便用户在浏览器里直接看到

如果该值是 `rgba(26,26,24,0.02)` 这种"看起来几乎是白的"颜色，也**必须保留**——它和纯白的差别在手机上非常明显，是这套排版的底色灵魂。

#### 写入模板（关键：粘贴到公众号编辑器才会保留）

**🔴 微信公众号编辑器粘贴时，只保留 inline `style=""` 属性，不保留 CSS class 里的样式。**

也就是说，如果背景色只写在 `body { background: ... }` 或 `.something { background: ... }` 里，浏览器里看着没问题，但**复制到公众号编辑器时背景会全部丢失**。同理：颜色、字号、行高、间距如果是装饰性的、希望粘贴后仍然有效，对**用户实际编辑的内容**最好都用 inline style，或者至少保证关键容器的背景以 inline style 写在元素上。

骨架已经做了正确的封装：
- `<article id="article">` 是浏览器外壳，不参与复制；它的 background 设为 `transparent`
- 内嵌一个 `<section id="article-body" style="background: <IMPORTANT_page_background>; padding: 16px 0;">`，**背景以 inline style 写在这个 section 上**
- "全选正文"按钮调用的 `selectArticle()` 选中的是 `#article-body`（不是 `#article`），所以复制走的是带 inline 背景的内容

AI 生成模板时务必：
1. 把 `<section id="article-body" style="background: rgba(26,26,24,0.02); ...">` 里的占位背景**替换成 `IMPORTANT_page_background` 的真实值**
2. 不要把背景色挪去 `:root --color-bg-page` 然后从 `#article-body` 上删 inline style
3. 如果原文还有特殊的整体 padding（比如左右内边距），一并写到这个 inline style 里

### 调色板
- `--color-accent-1` 主色（出现频次最高的强调色）
- `--color-accent-2` 辅色（第二常用的强调色，可选）
- `--color-text` 正文
- `--color-heading` 标题
- `--color-text-secondary` 次要文字（图注、作者信息）
- `--color-text-muted` 辅助信息
- `--color-bg-page` 页面底（通常白色或浅米）
- `--color-bg-emphasis` 强调框底色
- `--color-bg-quote` 引用底色
- `--color-bg-code` 代码底色
- `--color-border` 默认边框色
- `--color-link` 超链接色

不要只捞一个主色就交差。从原文所有 `style="color:..."`、`background`、`border-color` 抽完出现次数 ≥2 的颜色并归类，缺失的类别要根据整体风格补齐。

### 字体系统
- `--font-body` 正文字族（公众号常见：`-apple-system, "PingFang SC", "Microsoft YaHei"`；如果原文刻意用了衬线或等宽，必须保留）
- `--font-heading` 标题字族
- `--font-mono` 代码字族
- `--font-size-body` 正文字号（常见 15/16/17/18px）
- `--font-size-h1/h2/h3` 三级标题
- `--font-size-caption` 图注/辅助信息字号
- `--line-height-body` 正文行高
- `--letter-spacing-body` 正文字间距（公众号爱用 0.5~1px 的字间距营造宽松感）
- `--font-weight-heading` 标题字重

### 间距系统
- 段落上下 margin
- 标题上下 margin（不同层级可能不一样）
- 图片上下 margin
- 列表项间距
- 引用块 padding / margin
- 强调框 padding

### 标题样式（逐级描述）
每一级标题描述成结构化的一段，比如：
- H2：居中；字号 20px；深色背景 `var(--color-heading)` + 白字；左右各 16px padding；上下 10px padding；圆角 4px；前后各 28px 外边距
- H3：左对齐；靠左有一条 4px 宽 `var(--color-accent-1)` 竖线；左内边距 12px；字号 17px；字重 600

不要只记"h2 居中"就完事，要记到能照着写 CSS 的程度。

### 组件清单
对照 `references/component-patterns.md` 的图鉴，把原文里出现的每一类组件都识别出来，为每类定义一个语义化 class，并写清：
- 用途（什么时候用这个组件）
- 视觉描述
- 完整 CSS

常见组件（不是全都有，有哪些要靠你识别）：
`.emphasis-box` 强调框｜`.key-point` 重点框｜`.step-num` 步骤序号｜`.divider` 装饰分割线｜`.callout-*` 不同语义的提示框｜`.quote-card` 引用卡｜`.label-good` `.label-bad` 好坏标签｜`.inline-highlight` 行内高亮｜`.inline-accent` 行内着色｜`.caption` 图注｜`.author-card` 作者/公众号卡片｜`.section-number` 章节编号

### 行内强调
原文里的 `<strong>`、`<em>`、带颜色的 `<span>`、带背景的 `<span>`——都要记清用了什么颜色、是否有下划线、是否有半透明背景条。公众号文章里这些"小标记"非常多，经常是它视觉辨识度的关键。

### 图片 / 图注
- 图片默认宽度（100%？居中？最大宽度？）
- 圆角
- 阴影
- 上下 margin
- 图注：是否有、字号、颜色、对齐方式、与图片的距离

### 列表
- 项目符号（默认圆点？自定义符号？方块？）
- 项目符号颜色
- 缩进
- 项之间的间距

### 装饰元素
- 分割线是 `<hr>`、一张小图还是 Unicode 符号（如 `· · ·`、`✦ ✦ ✦`、`━━━`）
- 标题前后是否有装饰符
- 首段是否下沉/加大/特殊处理

---

## 模板产出要求

模板是一份 **自包含、零依赖、浏览器直接打开能看** 的 HTML 文件，结构大致如下：

```
<!DOCTYPE html>
<html>
<head>
  <style>
    :root { /* 所有 CSS 变量 */ }
    /* 通用样式 */
    /* 标题 */
    /* 组件 class */
    /* 行内样式 */
    /* 图片 */
    /* 列表 */
    /* 打印/复制友好 */
  </style>
</head>
<body>
  <div class="toolbar">[ 全选正文 ] 按钮 + 使用说明</div>
  <article id="article">
    <!-- demo 正文，覆盖所有组件 -->
  </article>
</body>
</html>
```

关键要求：

- **所有样式必须 inline 在 `<style>` 里**，不引用外部 CSS/字体/图片
- **CSS 变量放在 `:root`**——下次用户想微调，改变量就行
- **demo 正文要全面**——每一个识别出的组件都要出现至少一次，这样用户打开模板能直观看到每个组件的样子，也能当"复制粘贴字典"用。**特别强调**：代码块（`.code-block`）和分割线（`.section-divider` 或 `.divider`）必须在 demo 里出现，因为它们是公众号排版里最容易遗漏、但又最常用到的组件
- **背景必须以 inline style 写在 `#article-body` 上**，不要只在 CSS class/变量里写背景——公众号编辑器粘贴时会丢掉 class 样式（详见上文"全局背景色"小节）
- **右上角放一个"全选正文"按钮**，点击后用 Range API 选中 `#article-body`（不是 `#article`），然后提示"Ctrl/Cmd+C 复制"（公众号编辑器支持粘贴富文本）
- **文件头部放一段注释**，包含：
  - 原文 URL 和标题
  - 设计语言摘要（两三句话说清这套排版的个性）
  - 色板、组件清单
  - 生成时间
- **class 名必须语义化**，不要写 `.box1` `.style2` 这种。语义化的 class 日后用户写新文章时才记得住怎么用。

---

## 复刻报告模板

生成完模板后，给用户一份简短的报告（控制在 200 字左右）：

```
✅ 排版复刻完成

模板：templates/{style-name}.html
原文：《xxx》by @xxx

设计语言：
  • 主色 #XXXXXX（陶土橘），辅 #XXXXXX（墨绿）
  • 衬线标题 + 无衬线正文，字号 16/18/22
  • 宽松的字间距（0.6px）和行高（1.9），读感舒缓
  • 章节之间用「· · ·」装饰性分割

识别出的组件（共 N 个）：
  .emphasis-box  — 左竖线+浅橘底的提醒框
  .step-num      — 陶土橘圆形数字，用于步骤
  .divider-dots  — 居中的装饰点分割线
  ...

下一步：
  在浏览器打开模板预览 → 把正文替换成你的新稿 → 点"全选正文"复制到公众号编辑器
```

---

## 遇到抓不到的情况

公众号反爬偶尔会返回"环境异常"页面。如果 `fetch.py` 抓到的内容不像正文（比如很短、没有 `js_content`、出现"请在微信客户端打开链接"），尝试：

1. 让用户在浏览器打开文章→右键→"查看网页源代码"→保存为 `.html` 文件→把路径给你
2. 你直接读这个本地文件走后续流程

不要反复 curl 同一个 URL 或编造假数据。

---

## 文件清单

```
wechat-layout-cloner/
├── SKILL.md                        # 本文档
├── scripts/
│   └── fetch.py                    # 抓取 + 提取 HTML 内容和样式
├── templates/
│   ├── _skeleton.html              # 模板骨架（生成新模板时基于此）
│   └── {AI 生成的模板}.html        # 每次复刻后新增
├── references/
│   ├── component-patterns.md       # 公众号常见组件图鉴（参考这个识别组件）
│   └── extraction-guide.md         # 系统化的分析 checklist
└── workspace/
    └── {slug}/                     # 每篇原文的临时工作目录
        ├── raw.html                # 抓到的完整 HTML
        ├── content.html            # 仅正文
        ├── styles.css              # 抽出的 <style> 内容
        └── meta.json               # 标题/作者/URL/时间
```

**读文件的时机：**
- 开始工作前：先读 `references/component-patterns.md`（组件图鉴）
- 填规格表时：配合 `references/extraction-guide.md`（分析清单）
- 生成模板时：读 `templates/_skeleton.html`（骨架）

---

## 示例调用

用户：
> https://mp.weixin.qq.com/s/cIxQ9gQg2EJLpJx8ZFxesQ 帮我把这篇排版扒下来做个模板

你：
1. 跑 `python scripts/fetch.py <url>`
2. 读 `references/component-patterns.md`
3. 读 `workspace/{slug}/content.html` + `styles.css`
4. 按规格表系统性分析（不要跳步）
5. 读 `templates/_skeleton.html`
6. 生成 `templates/{name}.html`
7. 输出复刻报告
