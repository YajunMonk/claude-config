# 公众号组件图鉴（Component Patterns）

识别组件之前先读完这份图鉴。公众号文章的排版工具（秀米、135编辑器、i排版、Markdown 生成器、少数作者手写 CSS）产出的 HTML 特征不一样，但**视觉组件的类型是高度收敛的**。下面列的是高频出现的几类，连同它们在 HTML 里的典型形态。你的任务是看原文 HTML 时逐一对照，把原文里用到的类型归类、记录、命名。

## 如何读这份文档

每个组件条目包含四部分：

- **视觉描述**：长什么样
- **语义用途**：什么时候用它
- **HTML 特征**：在抓到的 HTML 里长什么样（这个最关键——没有标签语义，全靠 inline style 识别）
- **建议的 class 名**：产出模板时用哪个

如果原文里某个东西你在下面找不到对应项，照样识别并命名——图鉴不是封闭集合，只是起个头。

---

## 1. 强调框类（Callout / Emphasis）

### 1.1 左竖线强调框

**视觉**：一段话，左边有一条 3~6px 宽的彩色竖线，整块通常有浅底色、轻微 padding。

**语义**：段落级的提醒、补充说明、重要结论、边栏笔记。

**HTML 特征**：
- 通常是 `<section>`、`<p>` 或 `<div>`
- inline style 有 `border-left: 3px|4px|5px solid #XXX`
- 可能还有 `background-color` 是浅色系
- 有 `padding` 或 `padding-left`

**建议 class**：`.emphasis-box` 或语义化的 `.note` / `.aside`

### 1.2 四边框卡片（Card）

**视觉**：整个段落被一个细边框围起来，或者有圆角 + 阴影，像一张卡片。

**语义**：引用、重点信息、案例小结。

**HTML 特征**：`border: 1px solid` + `border-radius` + 可能的 `box-shadow`

**建议 class**：`.card` / `.quote-card` / `.case-card`

### 1.3 带装饰符的提示框

**视觉**：卡片的左上角或前置有一个 Unicode 装饰符（✦、❖、💡、▍、📌）。

**语义**：核心观点、结论、警示。

**HTML 特征**：内部第一行或第一个 span 是一个特殊符号字符，通常加了 color 或 font-size。

**建议 class**：`.key-point` / `.callout-tip` / `.callout-warning`

### 1.4 分栏上下式（标题条 + 内容）

**视觉**：上面一条深色横条写标题，下面一段浅色区域是内容，像标签页头。

**语义**：小节标题 + 小节正文绑在一起。

**HTML 特征**：两个相邻的 `<section>`，第一个有深色 `background` 和白色 `color`，第二个有浅色 `background`。

**建议 class**：`.banner-box` + `.banner-title`

---

## 2. 标题组件

### 2.1 纯文字标题

**视觉**：没有底色装饰，纯字号 + 字重 + 颜色变化。

**HTML 特征**：`<h1>` / `<h2>` / `<h3>`，或 `<p>`/`<section>` 带着 `font-size` + `font-weight`。公众号导入的 HTML 常常**没有 h 标签**，标题全是 inline style 的 p。

### 2.2 底色标题

**视觉**：文字在彩色背景条里，通常白字 + 彩底，居中或左对齐。

**HTML 特征**：有 `background` + 对比色 `color` + 一定的 padding。

### 2.3 左竖线标题

**视觉**：左侧一条短竖线，右侧是标题文字。和 1.1 不同的是**这是标题，整行没有背景**。

**HTML 特征**：`border-left: 3~4px solid`，`padding-left: 8~12px`，字重较大。

### 2.4 居中装饰标题

**视觉**：居中文字，前后各有一个装饰符（`—— xxx ——`、`| xxx |`、`✦ xxx ✦`）或左右两侧有装饰短线。

**HTML 特征**：`text-align: center`，文字内容本身包含 Unicode 装饰符。或者通过伪元素/`<span>` 实现两侧装饰。

### 2.5 章节编号 + 标题

**视觉**：标题上方有一个小号彩色数字或英文标签（如 "01" / "SECTION 01" / "NO.01"），下面才是标题正文。

**语义**：强结构感的长文喜欢用。

**HTML 特征**：连续两行，第一行字号明显小，字重大，颜色是主色。

**建议 class**：`.section-number` + 正常标题

---

## 3. 列表增强

### 3.1 步骤序号（圆点/方块数字）

**视觉**：一个带背景色的小圆或方块，里面是数字，后面跟步骤描述。

**HTML 特征**：`<span style="display:inline-block; width:22px; height:22px; border-radius:50%; background:#XXX; color:#fff; text-align:center;">1</span>`

**建议 class**：`.step-num`

### 3.2 自定义项目符号

**视觉**：不是默认的 •，而是 `▍`、`▶`、`●`、主色方块等。

**HTML 特征**：`<ul>` 被 `list-style: none` 禁用默认符号，然后每个 `<li>` 的 `::before` 或前缀手动写了符号。或者干脆用 `<p>` 前置符号模拟列表。

### 3.3 好坏对照标签

**视觉**：小号字的"推荐/避免"、"Do/Don't"、"✓/✗"标签，后面跟内容。

**HTML 特征**：两个颜色（通常绿/红），带 padding 和圆角的小 span。

**建议 class**：`.label-good` / `.label-bad` 或 `.label-do` / `.label-dont`

---

## 4. 分割线

### 4.1 装饰字符分割线

**视觉**：`· · ·` / `— — —` / `✦ ✦ ✦` / `━━━` 居中一行。

**HTML 特征**：单独一个段落或 div，内容是重复的 Unicode 字符，通常 `text-align: center` + 字号偏大 + 有字间距。

**建议 class**：`.divider` 或 `.divider-dots` / `.divider-stars`

### 4.2 细线分割

**视觉**：一条极细的横线，可能有颜色。

**HTML 特征**：`<hr>` 或 `border-top: 1px solid` 的空 div / section。

### 4.3 图片分割线

**视觉**：一张装饰性小图（波浪、花纹、品牌标识）居中。

**HTML 特征**：`<img>` 宽度通常小于正文（如 60~200px），居中显示。

**建议 class**：`.divider-img`（如果用户选了不下载图片模式，模板里可以用 SVG 或 Unicode 近似）

---

## 5. 行内强调

### 5.1 彩色文字（inline accent）

**HTML 特征**：`<span style="color:#XXX">`，颜色不是黑色/灰色。常配 `font-weight: 600/700`。

**建议 class**：`.inline-accent`

### 5.2 高亮底色（inline highlight）

**HTML 特征**：`<span style="background:#XXX">`——通常半透明的主色或荧光色。

**建议 class**：`.inline-highlight`

### 5.3 下划波浪线

**HTML 特征**：`text-decoration-style: wavy` 或用 `background-image: linear-gradient` 模拟。

**建议 class**：`.inline-wavy`

### 5.4 着重号（中文传统强调）

**HTML 特征**：`text-emphasis: dot` 或 `text-emphasis-style: filled`。

### 5.5 删除线

**HTML 特征**：`<s>`、`<del>` 或 `text-decoration: line-through`。

---

## 6. 图片与图注

### 6.1 普通配图

- 通常居中
- 宽度 100% 或限制在正文宽度
- 圆角（0 / 4 / 8 / 12px 都常见）
- 可能有阴影
- 图片下方紧跟一段居中/左对齐的小号灰色文字作为图注

**图注 HTML 特征**：紧跟 `<img>` 之后的小字 `<p>` 或 `<span>`，`font-size` 12~14px，`color` 灰色。

**建议 class**：`.figure` 或直接用 `<figure>` + `<figcaption>`

### 6.2 分屏图（两图并列 / 三图网格）

**HTML 特征**：`display: flex` 或 table 结构，多个 img 并排。

### 6.3 全出血图（超出正文宽度）

**HTML 特征**：负 margin 或 `width: 100vw`。

---

## 7. 代码

### 7.1 行内代码

**HTML 特征**：`<code>` 或 `<span>` 带等宽字体 + 浅底色 + 轻微 padding。

### 7.2 代码块

**HTML 特征**：`<pre>` + `<code>` 或 `<section style="background: ...; font-family: monospace">`。常有语法高亮（每个 token 一个彩色 span）。

**注意**：公众号不支持 `<pre>` 原生，很多工具会展开成"一行一个 p"的形式。

---

## 8. 引用与来源

### 8.1 Markdown 风 blockquote

**HTML 特征**：`<blockquote>`，左侧竖线 + 浅灰底 + 次要文字色。

### 8.2 大引号卡片

**视觉**：大号的 `"`（unicode 201C）作为装饰符，整块有边框或阴影。

**HTML 特征**：有一个超大字号（40~80px）的装饰字符出现在卡片内部。

### 8.3 来源链接小字

**视觉**：引用末尾的 `—— 来源：xxx` 或 `@作者名`。

**HTML 特征**：右对齐或独立一行，小号字，次要文字色。

---

## 9. 作者 / 公众号卡片

**视觉**：文末或文中的小卡片，头像 + 名字 + 简介 + 可能的二维码/关注按钮。

**HTML 特征**：flex 布局，左头像右文字，整块有浅背景或边框。

**建议 class**：`.author-card`

---

## 10. 装饰元素（Easter Eggs）

一些作者有自己的视觉签名：
- 文章开头的作者签名栏（@xxx · 职业 · 日期）
- 文末的"写在最后"/"写作后记"装饰
- 首段下沉字（drop cap）
- 章节编号使用特殊符号（①②③ / 壹贰叁 / Ⅰ Ⅱ Ⅲ）
- 特殊的段首符号（▎／▍／▌）

**识别逻辑**：只要某个视觉元素出现了 **2 次以上** 并且它不在上面已分类的组件里，就单独为它起一个 class。**重复出现的视觉就是作者的设计语言。**

---

## 识别的 Checklist

完成组件识别时，对每一类问自己这三个问题：

1. 原文里出现了几次？（出现 2 次以上一定要在模板里保留成可复用组件）
2. 它的视觉属性有哪些？（颜色、粗细、位置、装饰符——写到能写出 CSS 的程度）
3. 语义上它承担什么任务？（是强调、分隔、引用、步骤……——这决定了你怎么命名 class）

**遗漏组件** 比 **多做组件** 更严重。宁可多识别几个，下次写新文章时用不上就空着，也比少一个关键组件要强。
