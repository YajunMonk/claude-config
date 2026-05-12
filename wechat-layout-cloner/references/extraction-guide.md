# 排版分析清单（Extraction Guide）

这是一份系统化的清单，指导你从抓到的 `content.html` + `styles.css` + `summary.json` 里填出一份完整的"排版规格"。读完 `component-patterns.md`（组件图鉴）后再读这份。

分析要**按顺序过清单**，不要跳着来——公众号的 HTML 没有语义，容易漏东西，清单是防漏网。

---

## 第零步（最先做）：提取全局背景色

**这是最容易漏掉、也最影响视觉效果的一个字段。**

公众号文章的全局背景色**通常不在 `<body>` 上，而在最外层的 `<section>` 上**，并且只出现一次，所以 `summary.json` 的 `top_colors` 频次统计里往往看不到它。但它决定了整篇文章的"底色气质"——白底和暖米底的差别是读者第一眼看到的东西。

**操作方法：**
1. 先看 `summary.json` 里的 `IMPORTANT_page_background` 字段——fetch.py 会单独提取这个值
2. 如果该字段有值（如 `rgba(26,26,24,0.02)` / `#f5f3ef` / `rgb(250,248,245)` 等），立刻用它设置：
   - `--color-bg-page`（CSS 变量）
   - 模板 `<body>` 的 `background-color`
   - 最外层文章容器 `#article` 也需要继承这个颜色
3. 如果该字段为空，打开 `content.html` 找第一行——看最外层 `<section>` 的 `style` 属性里有没有 `background`

**常见背景色形式：**
- `rgba(26,26,24,0.02)` — 极浅暖灰，非常常见，不要当白色处理
- `#f5f3ef` / `#faf8f5` — 米白
- `rgb(250,249,245)` — 奶油白
- `#fff` / `white` — 纯白（如果确认是纯白，也要明写，不要省略）

如果你不应用这个背景色，模板的整体气质会和原文相差很大，哪怕其他组件都对了。

---

## 第一步：先看 summary.json，建立总体印象

**注意**：`summary.json` 里新增了三个 `IMPORTANT_` 前缀字段——`IMPORTANT_page_background`、`IMPORTANT_code_blocks`、`IMPORTANT_dividers`——这三个是特别提取的，务必先读它们再往下走。

`summary.json` 里已经帮你统计好了：

- `top_colors`：出现频次最高的 30 个颜色（hex + rgb）
- `top_font_sizes`：出现频次最高的字号
- `top_line_heights`、`top_letter_spacings`
- `top_font_families`：字族
- `top_classes`：出现频次最高的 class（公众号导入工具会生成，但通常没有语义）
- `tag_counts`：标签分布

花 30 秒扫一遍，回答这几个问题：

- **颜色风格**是什么？暖色 / 冷色 / 黑白灰 / 马卡龙 / 高饱和 / 低饱和？
- **主色**大概是什么？（`top_colors` 里排第一的彩色——过滤掉黑色 #000/#141413、白色 #fff、灰色系后的第一个有饱和度的颜色）
- **字号档位**有几档？（通常 3~4 档：图注字号 < 正文 < 小标题 < 大标题）
- **字体**是系统默认，还是刻意用了衬线（`serif` / `宋体` / `Georgia`）或其他非常规字族？
- **字间距/行高**有没有刻意设计？（正文 `letter-spacing` 0 和 `letter-spacing: 1px` 的观感差别非常大）

写一段 3~5 行的**设计语言摘要**（后面生成模板报告也要用），示例：

> 暖色调杂志风：主色陶土橘（rgb(217,119,87)），搭配墨绿辅色；正文 16px，行高 1.9，字间距 0.6px，呈现宽松的阅读节奏；标题用较粗的字重但不加背景色，靠字号和竖线装饰区分层级。

---

## 第二步：填调色板（所有 12 个变量）

照 SKILL.md 的变量表逐项填。方法：

1. `--color-accent-1`：`top_colors` 里频次最高、且饱和度 > 20% 的颜色
2. `--color-accent-2`：频次第二、和主色不是同一色相的彩色
3. `--color-text`：出现在段落 `color: #XXX` 里、接近黑色的那个（常见 `#141413` / `#333` / `#262626`）
4. `--color-heading`：标题文字的颜色（通常比正文深一点）
5. `--color-text-secondary`：图注、引用里出现的灰色
6. `--color-text-muted`：更浅的灰色，用于作者信息/辅助文字
7. `--color-bg-page`：默认 `#fff`，除非原文明显是米色/米白底
8. `--color-bg-emphasis`：强调框里用的浅底色（通常是主色的极浅版本，饱和度 < 15%）
9. `--color-bg-quote`：引用块的底色
10. `--color-bg-code`：代码块的底色
11. `--color-border`：框的边框色
12. `--color-link`：如果原文有超链接，抽其颜色；否则用主色

**注意**：颜色的归类不是机械的"出现次数最多=主色"。`#000000` 可能出现 1000 次，但那是正文；你要找的是**在视觉上承担'强调'角色的那个彩色**。

---

## 第三步：字体系统

- `--font-body`：正文字族，从 `top_font_families` 抽。如果没有特殊的，用 `-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif`
- `--font-heading`：如果标题用了不同字族（少见但存在），单独抽；否则等于 `var(--font-body)`
- `--font-mono`：如果原文有代码块，抽其字族；否则 `"SF Mono", Menlo, Consolas, monospace`
- `--font-size-body`：`top_font_sizes` 里频次最高的那个（公众号常见 15/16/17/18px）
- `--font-size-h1/h2/h3`：按标题出现时的 `font-size`。如果原文没有三级标题，保留骨架里的默认值但降一档对应
- `--font-size-caption`：图注/作者信息的字号（通常 12~14px）
- `--line-height-body`：`top_line_heights` 第一名（常见 1.6~2.0）
- `--letter-spacing-body`：`top_letter_spacings` 第一名（常见 0~1.5px）
- `--font-weight-heading`：标题出现时的 `font-weight`（常见 500/600/700）

---

## 第四步：标题样式（逐级细化）

扫一遍 `content.html` 找所有看起来像标题的块（`<h1>~<h6>` 或 inline style 指定大字号 + 粗体的 `<p>`/`<section>`）。对每一级标题回答：

- **对齐**：左 / 居中 / 右
- **颜色**：字色是什么，背景色是什么
- **装饰**：左侧有竖线吗？前后有装饰符吗？有下划线吗？
- **形状**：有圆角的背景块吗？有边框吗？
- **上下间距**：大概多少 em / px

把这些写进模板的对应 CSS 里，不要只留骨架的默认。

---

## 第五步：段落与间距

- 段落上下间距（`<p>` 的 `margin`）
- 首行缩进（中文公众号基本没有，但要记一下）
- 段落之间是否有空行（用 `margin` 模拟）
- 段与标题之间的距离

---

## 第六步：组件识别（最关键）

**对照 `component-patterns.md`**，逐项扫 `content.html`：

- 搜 `border-left` → 可能是强调框或左竖线标题
- 搜 `background:` 且带浅色 → 可能是强调框或卡片
- 搜 `border-radius: 50%` → 可能是步骤圆点
- 搜特殊 Unicode（`· · ·` / `━` / `✦` / `❖` / `▍` / `▶`）→ 可能是分割线或前缀装饰
- 搜 `text-emphasis` → 中文着重号
- 搜两个连续 `<section>` 中第一个有深色背景 → banner-box 标题 + 内容

**判断标准**：某个视觉元素**出现 ≥2 次**就值得单独做成 class。出现 1 次的可以写进模板的 demo 里当一次性样式，但不做可复用 class。

为每个识别出的组件填写：
- 语义化 class 名（避免 `.box1` / `.style-3`）
- 完整 CSS
- 在 demo 正文里出现一次，方便用户看样

---

## 第七步：行内强调

扫 `content.html` 里所有的 `<span>`，按 inline style 分组：

- 带 `color:` 且不是黑色：`.inline-accent`
- 带 `background:`：`.inline-highlight`
- 带 `text-decoration:`：下划线 / 波浪线 / 删除线
- 中文着重号：`text-emphasis`

每类都在模板的 demo 里用一次。

---

## 第八步：图片、列表、代码、引用、分割线

按骨架里的对应 section，根据原文实际样式调整。

### 图片
- 圆角（常见 6/8/12px）
- margin-top / margin-bottom
- 是否有阴影（`box-shadow`）
- 宽度（100% / 限制最大宽 / 居中）

### 图注
- 字号（通常 12~14px）
- 颜色
- 对齐方式（居中最常见）
- 与图片的距离

### 列表
- 项目符号样式——`summary.json` 的 `IMPORTANT_dividers` 里的 `arrow-list` 模式（`→` 前缀）是一种变形列表
- 列表项间距
- 是否用 `<section>` 而不是 `<ul>` 来模拟列表（公众号常见）

### 代码块（公众号特殊）

**重要**：公众号不支持 `<pre>` 标签，代码块通常是：
- `<section style="font-family: 'JetBrains Mono',... ; background: ...">` 的多行结构
- 或者多个等宽字体的 `<p>` 堆叠

**识别方法**：先看 `summary.json` 里的 `IMPORTANT_code_blocks` 字段——fetch.py 已经帮你找到了等宽字体的 section。如果有，就读它的：
- `background`：代码块底色
- `font_size`：字号
- `color`：代码文字颜色
- `padding`：内边距

在模板里定义 `.code-block` class，用来模拟这种结构（用 `<div class="code-block"><code>…</code></div>` 的方式）。

### 引用块
- 普通 blockquote：左竖线 + 浅底 + 次要文字色
- 大型引用卡（带边框或阴影）：四边框 + 圆角
- 来源注释（引用末尾的小字）

### 分割线（不要漏！）

**重要**：先看 `summary.json` 里的 `IMPORTANT_dividers` 字段——fetch.py 已经提取了分割线的类型和样式。常见形式：

**类型 1：细线分割（最常见）**
- HTML 特征：`<section style="border-top: 1px solid rgba(...);">` + `height:0`
- CSS：`.section-divider { border-top: 1px solid rgba(120,120,112,0.18); margin: 24px 0; }`

**类型 2：Unicode 装饰符分割**
- 内容：`· · ·` / `✦ ✦ ✦` / `━━━━━` / `— — —` 等
- 通常居中、有字间距

**类型 3：图片分割**
- 一张小装饰图（宽度 60~200px，居中）
- 模板里用 Unicode 近似或留一个 `.divider-img` 的容器

每种分割线都要定义 class 并在 demo 里出现一次。

---

## 第九步：装饰资产（Easter Eggs）

这是最容易漏的部分。扫一遍文章里那些"重复出现的视觉签名"：

- 开篇是否有作者签名栏
- 文末是否有固定的结束语/落款
- 章节之间是否有固定的装饰分隔
- 正文里是否频繁出现特定 emoji 或符号（`| xx |`、`【xx】`、`› xx ‹` 这种）

这些很能体现作者风格，遗漏会让复刻"不像"。

---

## 第十步：生成模板

基于 `templates/_skeleton.html` 修改：

1. 替换所有 `{{...}}` 占位符
2. 改写 `:root` 里的 CSS 变量
3. 改写标题、段落、引用、列表、代码、图片的 CSS
4. 添加/删除组件 class——骨架里有一批默认的，保留用得上的，删掉用不上的，添加骨架里没有但原文有的
5. 改写 `<article>` 里的 demo 正文，让每个组件都出现至少一次

**起一个有辨识度的文件名**。命名风格建议：

- `{色彩关键字}-{版面关键字}-{质感关键字}.html`
- 例子：`warm-orange-magazine.html` / `minimal-mono-grid.html` / `serif-editorial-black.html` / `pastel-cards-playful.html` / `tech-mint-compact.html`

---

## 质量自检（生成完模板后）

在交付前，快速检查：

- [ ] 模板在浏览器里打开正常渲染（没有报错、没有外链破图）
- [ ] demo 正文覆盖了每一个识别出的组件
- [ ] 所有 CSS 变量都赋值了，没留占位符
- [ ] 文件头注释完整（URL、标题、作者、设计语言摘要、组件清单、生成时间）
- [ ] 没有留下 `{{...}}` 这类占位符
- [ ] class 名都是语义化的（不是 .box1 / .style2）
- [ ] 右上角的"全选正文"按钮能用

自检通过才输出复刻报告给用户。
