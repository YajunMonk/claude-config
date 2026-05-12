#!/usr/bin/env python3
"""
公众号文章抓取器（wechat-layout-cloner）

职责：
  1. 抓 HTML
  2. 抽正文 #js_content
  3. 抽 <style> 标签的全部内容
  4. 抽元信息（标题/作者/公众号名/发布时间）
  5. 做一些基础的统计给 AI 参考（颜色频次、字号频次、class 频次）
  6. 保存到 workspace/{slug}/ 下

AI 做的事：读取这些产物后做组件识别、规格填写、模板生成。
"""

import sys
import re
import json
import subprocess
import hashlib
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def fetch_html(url: str) -> str:
    result = subprocess.run(
        ["curl", "-sL", "-A", USER_AGENT, url],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0 or not result.stdout:
        print(f"❌ curl 失败（returncode={result.returncode}）", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def extract_meta(html: str) -> dict:
    def first_match(pattern, default=""):
        m = re.search(pattern, html, re.DOTALL)
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else default

    title = first_match(r'<h1[^>]*class="[^"]*rich_media_title[^"]*"[^>]*>(.*?)</h1>')
    author = first_match(r'<a[^>]*id="js_name"[^>]*>(.*?)</a>') or first_match(
        r'<span[^>]*class="[^"]*rich_media_meta_nickname[^"]*"[^>]*>(.*?)</span>'
    )
    publish_time = first_match(r'<em[^>]*id="publish_time"[^>]*>(.*?)</em>') or first_match(
        r'var\s+ct\s*=\s*"(\d+)"'
    )
    return {
        "title": title or "(未知标题)",
        "author": author or "(未知作者)",
        "publish_time": publish_time,
    }


def extract_content(html: str) -> str:
    """抽 #js_content 里的正文 HTML。"""
    # 主要情况：id="js_content"
    m = re.search(
        r'id="js_content"[^>]*>(.*?)</div>\s*</div>\s*<script',
        html,
        re.DOTALL,
    )
    if m:
        return m.group(1).strip()
    # 退化：找 rich_media_content
    m = re.search(
        r'class="[^"]*rich_media_content[^"]*"[^>]*>(.*?)</div>\s*</div>\s*<script',
        html,
        re.DOTALL,
    )
    if m:
        return m.group(1).strip()
    return ""


def extract_styles(html: str) -> str:
    """抽页面所有 <style>…</style> 的内容并拼起来。"""
    styles = re.findall(r"<style[^>]*>(.*?)</style>", html, re.DOTALL)
    return "\n\n/* ---- next style block ---- */\n\n".join(styles)


# -------- 统计：让 AI 一眼看到调色板 / 字号分布 / 高频 class --------

COLOR_RE = re.compile(
    r"(?:color|background|background-color|border|border-color|border-[a-z]+-color)\s*:\s*"
    r"([^;\"']+)",
    re.IGNORECASE,
)
HEX_COLOR = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}\b")
RGB_COLOR = re.compile(r"rgba?\([^)]+\)")
FONT_SIZE = re.compile(r"font-size\s*:\s*([^;\"']+)", re.IGNORECASE)
LINE_HEIGHT = re.compile(r"line-height\s*:\s*([^;\"']+)", re.IGNORECASE)
LETTER_SPACING = re.compile(r"letter-spacing\s*:\s*([^;\"']+)", re.IGNORECASE)
CLASS_ATTR = re.compile(r'class="([^"]+)"')
TAG_RE = re.compile(r"<([a-zA-Z][a-zA-Z0-9]*)\b")


def extract_page_background(content: str) -> str:
    """
    提取页面/文章的全局背景色。

    公众号文章的背景色通常设在最外层 <section> 上（而非 <body>），
    且往往只出现一次，所以在频次统计里看不到——需要单独提取。

    判断策略：找第一个设了 background 的 section/div，且该 background
    不是透明/白色/rgba(0,0,0,0)。
    """
    # 找最外层 section 的 background
    outer = re.match(r"<section[^>]+>", content, re.IGNORECASE)
    if outer:
        tag_html = outer.group(0)
        bg = re.search(r"background\s*:\s*([^;\"'>]+)", tag_html, re.IGNORECASE)
        if bg:
            val = bg.group(1).strip()
            if val not in ("transparent", "none", "inherit", "initial", "rgba(0,0,0,0)"):
                return val

    # 再往后找几个 section/div，取第一个有 background 且面积大的
    candidates = re.findall(
        r"<(?:section|div)[^>]+background\s*:\s*([^;\"'>]+)[^>]*>",
        content[:5000],  # 只看前 5000 字符
        re.IGNORECASE,
    )
    for val in candidates:
        val = val.strip()
        if val and val not in ("transparent", "none", "inherit", "initial", "rgba(0,0,0,0)"):
            return val
    return ""


def extract_code_blocks(content: str) -> list:
    """
    提取公众号里模拟代码块的元素。

    公众号不支持原生 <pre>，代码块有两种常见形式：
    1. <section style="font-family: Mono/Consolas...">  —— section 套多行 p
    2. <p style="font-family: Mono/Consolas...">        —— 每行一个 p（更常见）

    还有一种是带背景色的整块 section（"提示词"灰框等）：
    3. <section style="background: rgba(XX,XX,XX,0.X); border-radius: Xpx; padding: ...">
    """
    results = []
    seen_bgs = set()

    # 形式 1 & 2：等宽字体的 section 或 p
    for tag in ("section", "p"):
        for m in re.finditer(rf"<{tag}([^>]*)>", content, re.IGNORECASE):
            attrs = m.group(1)
            # 等宽字体特征（注意 HTML 实体 &#39; 和普通引号都要匹配）
            if re.search(r"(?:Mono|Consolas|Menlo|Courier|monospace)", attrs, re.IGNORECASE):
                bg = re.search(r"background(?:-color)?\s*:\s*([^;\"'>]+)", attrs, re.IGNORECASE)
                font_size = re.search(r"font-size\s*:\s*([^;\"'>]+)", attrs, re.IGNORECASE)
                color_m = re.search(r"(?<![a-z-])color\s*:\s*([^;\"'>]+)", attrs, re.IGNORECASE)
                bg_val = bg.group(1).strip() if bg else ""
                results.append({
                    "tag": tag,
                    "background": bg_val,
                    "font_size": font_size.group(1).strip() if font_size else "",
                    "color": color_m.group(1).strip() if color_m else "",
                    "note": f"Monospace {tag} — likely code line or label",
                })
                if len(results) >= 3:
                    break
        if results:
            break

    # 形式 3：有背景色的整块容器（灰框/提示词框等）
    for m in re.finditer(r"<section([^>]*)>", content, re.IGNORECASE):
        attrs = m.group(1)
        bg = re.search(r"background(?:-color)?\s*:\s*(rgba?\([^)]+\))", attrs, re.IGNORECASE)
        if bg:
            val = bg.group(1).strip()
            # 排除页面背景（rgba(26,26,24,0.02)）和红色强调框
            if val in seen_bgs:
                continue
            opacity_m = re.search(r"rgba?\([^,]+,[^,]+,[^,]+,\s*([\d.]+)\)", val)
            opacity = float(opacity_m.group(1)) if opacity_m else 1.0
            # 只收录不透明度 0.03~0.15 的中性背景（灰框/内容块）
            if 0.03 <= opacity <= 0.15:
                br = re.search(r"border-radius\s*:\s*([^;\"'>]+)", attrs, re.IGNORECASE)
                p = re.search(r"padding\s*:\s*([^;\"'>]+)", attrs, re.IGNORECASE)
                results.append({
                    "tag": "section",
                    "background": val,
                    "border_radius": br.group(1).strip() if br else "",
                    "padding": p.group(1).strip() if p else "",
                    "note": "Tinted container block (code-box / prompt-box / callout)",
                })
                seen_bgs.add(val)
                if len(results) >= 5:
                    break

    return results


def extract_dividers(content: str) -> list:
    """
    提取分割线结构。公众号的分割线通常是：
    1. <section> with border-top + height:0（细线）
    2. 居中的 Unicode 装饰符（· · · / ━ / ✦ 等）
    3. 装饰性小图片
    """
    results = []

    # 类型 1：border-top + height:0 细线
    for m in re.finditer(
        r"<section([^>]*border-top[^>]*)>",
        content,
        re.IGNORECASE,
    ):
        attrs = m.group(1)
        border = re.search(r"border-top\s*:\s*([^;\"'>]+)", attrs, re.IGNORECASE)
        if border:
            results.append({"type": "line", "style": border.group(1).strip()})
            break

    # 类型 2：Unicode 装饰符居中段落
    unicode_dividers = re.findall(
        r"text-align\s*:\s*center[^>]*>([·•✦✧━─—*▪▫◆◇○●]{2,}[^<]{0,20})</",
        content,
        re.IGNORECASE,
    )
    if unicode_dividers:
        results.append({"type": "unicode", "content": unicode_dividers[0].strip()})

    # 类型 3：连续重复的 Unicode 字符（不需要 text-align 标记）
    symbol_dividers = re.findall(
        r">([·•✦✧━─—]{1}[·•✦✧━─— ]{3,})</",
        content,
    )
    if symbol_dividers and not any(d["type"] == "unicode" for d in results):
        results.append({"type": "unicode", "content": symbol_dividers[0].strip()})

    return results


def summarize(content: str, styles: str) -> dict:
    combined = content + "\n" + styles

    # 颜色：分别抓 hex 和 rgb 形式
    colors = Counter()
    for m in HEX_COLOR.findall(combined):
        colors[m.lower()] += 1
    for m in RGB_COLOR.findall(combined):
        colors[re.sub(r"\s+", "", m.lower())] += 1

    font_sizes = Counter(s.strip() for s in FONT_SIZE.findall(combined))
    line_heights = Counter(s.strip() for s in LINE_HEIGHT.findall(combined))
    letter_spacings = Counter(s.strip() for s in LETTER_SPACING.findall(combined))

    classes = Counter()
    for attr in CLASS_ATTR.findall(content):
        for c in attr.split():
            classes[c] += 1

    tags = Counter(TAG_RE.findall(content))

    # 把常用的 font 家族也统计一下
    fonts = Counter()
    for m in re.finditer(r"font-family\s*:\s*([^;\"']+)", combined, re.IGNORECASE):
        fonts[m.group(1).strip()] += 1

    def top(counter, n=20):
        return counter.most_common(n)

    # 特殊提取：背景色、代码块、分割线（这些容易被频次统计漏掉）
    page_bg = extract_page_background(content)
    code_blocks = extract_code_blocks(content)
    dividers = extract_dividers(content)

    return {
        "IMPORTANT_page_background": page_bg,
        "IMPORTANT_code_blocks": code_blocks,
        "IMPORTANT_dividers": dividers,
        "top_colors": top(colors, 30),
        "top_font_sizes": top(font_sizes, 15),
        "top_line_heights": top(line_heights, 10),
        "top_letter_spacings": top(letter_spacings, 10),
        "top_font_families": top(fonts, 10),
        "top_classes": top(classes, 40),
        "tag_counts": top(tags, 30),
    }


def slug_from(url: str, title: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", title).strip("-")[:40]
    if not base:
        base = "article"
    h = hashlib.md5(url.encode()).hexdigest()[:6]
    return f"{base}-{h}"


def write(path: Path, data: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 fetch.py <微信文章URL> [--workspace <dir>]")
        sys.exit(1)

    url = sys.argv[1]

    if not urlparse(url).netloc:
        print("❌ URL 格式不对")
        sys.exit(1)

    # 允许本地 html 文件（反爬兜底方案）
    if url.startswith("file://") or url.endswith(".html"):
        local_path = url.replace("file://", "")
        html = Path(local_path).read_text(encoding="utf-8")
        print(f"📄 从本地读取: {local_path} ({len(html):,} 字符)")
    else:
        print(f"📥 抓取: {url}")
        html = fetch_html(url)
        print(f"✓ 抓到 {len(html):,} 字符")

    meta = extract_meta(html)
    print(f"📝 标题: {meta['title']}")
    print(f"✍️  作者: {meta['author']}")

    content = extract_content(html)
    if not content:
        print("❌ 没找到正文（#js_content），可能被反爬或文章已删除")
        print("   兜底方案：让用户在浏览器打开 → 查看源代码 → 保存为 .html → 把路径传进来")
        sys.exit(2)
    print(f"✓ 正文 {len(content):,} 字符")

    styles = extract_styles(html)
    print(f"✓ 样式表 {len(styles):,} 字符")

    summary = summarize(content, styles)

    skill_dir = Path(__file__).resolve().parent.parent
    workspace = skill_dir / "workspace" / slug_from(url, meta["title"])
    workspace.mkdir(parents=True, exist_ok=True)

    write(workspace / "raw.html", html)
    write(workspace / "content.html", content)
    write(workspace / "styles.css", styles)
    write(
        workspace / "meta.json",
        json.dumps({"url": url, **meta}, ensure_ascii=False, indent=2),
    )
    write(
        workspace / "summary.json",
        json.dumps(summary, ensure_ascii=False, indent=2),
    )

    print()
    print(f"📁 工作目录: {workspace}")
    print("   ├─ content.html   （正文 HTML）")
    print("   ├─ styles.css     （页面所有 <style>）")
    print("   ├─ meta.json      （标题/作者/URL/时间）")
    print("   └─ summary.json   （颜色/字号/class 频次统计，AI 参考）")
    print()
    print("✅ 抓取完成。下一步由 AI 读取 content.html + summary.json 做组件识别和模板生成。")

    # 把 workspace 路径以机器可读形式输出（方便下游脚本/AI 获取）
    print(f"\nWORKSPACE={workspace}")


if __name__ == "__main__":
    main()
