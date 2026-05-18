---
name: daily-entertainment-observation
description: Create or update a dated Chinese entertainment observation report and deliver it as a long vertical-share PNG image for brand marketing teams. Use when the user asks for today's or this week's entertainment observation, wants to refresh the existing `阿叫一周娱乐热度观察` template, or wants a repeatable workflow that updates top stars, variety shows, film/TV, brand fit, risk status, and collaboration suggestions in a decision-ready format. Always enforce the original HTML template and rendered PNG QA; do not accept hand-drawn, PIL/canvas, offline-cloned, or visually redesigned fallback images as final deliverables.
---

# Daily Entertainment Observation

Create the dated working HTML first, then render the final deliverable as a long PNG image. Keep the output direct, polished, and ready to share internally.
Default output names must be date-prefixed, for example `260423-阿叫一周娱乐热度观察.html` and `260423-阿叫一周娱乐热度观察.png`. If a same-day file already exists, create a new suffixed pair such as `260423-阿叫一周娱乐热度观察-02.html`.

## Workflow

1. Resolve the output workspace.
Use the active workspace by default. Create a new date-prefixed report file in the current workspace root unless the user specifies another directory. If the same-day filename already exists, create a new suffixed file instead of overwriting it. Do not update an old report in place unless the user explicitly asks to overwrite a specific file.

2. Build today's report in one step.
Prefer `scripts/build_daily_observation.py --output-dir <dir> --render`. It will fetch current signals, update the HTML, and render the final PNG in one run.
If you have ALAPI access, pass `--alapi-token <token>` or set `ALAPI_TOKEN` first to add structured `今日热榜`、`微博热搜榜` and `头条热搜` signals.

When a full workflow copy exists in the workspace, prefer that copy, for example:

```bash
python3 daily-entertainment-observation/scripts/build_daily_observation.py --output-dir <workspace> --render
```

If only offline helper scripts exist at `<workspace>/scripts`, do not treat them as final-delivery scripts. Look for the full skill/project script under `<workspace>/daily-entertainment-observation/scripts/` or the installed skill path first.

3. Use the helper scripts only as fallbacks.
If you need finer control, you can still use:
- `scripts/create_daily_observation.py --output-dir <dir>`
- `scripts/render_observation_png.py --html <path/to/html>`

4. Keep the report auto-first.
The build script should be the default path, not manual copy edits, unless the user explicitly wants hand-tuned content.

5. Write for brand decision-making.
Keep wording direct and concise. Remove process language such as "this version", "sample", "free plan", "explanation", "observation caliber", or anything that sounds like production notes.

6. Preserve the template structure.
Do not redesign the layout unless the user asks. Keep the `阿叫热点榜` daily format, the red-orange premium hero area, the long vertical-share composition, and the same section sequence: hero, `今日热点`, `明星推荐`, `热搜人名观察`, `补充观察`, closing summary.

7. Enforce a hard delivery gate before reporting completion.
Never mark the job done just because a `.png` file exists. Verify that the final PNG is a browser-rendered image from the corresponding HTML source and that it matches the original template geometry. The previous accepted daily template renders around `1082px` wide and a long vertical height around `13619px`; the exact height can drift slightly with content, but a `900px`-wide, sub-1MB, or manually composed image is not acceptable.

Run checks like:

```bash
ls -lh <html> <png>
file <png>
python3 - <<'PY'
from PIL import Image
from pathlib import Path
png = Path("<png>")
im = Image.open(png)
print(im.size, png.stat().st_size)
PY
```

Also check the HTML contains `阿叫热点榜`, `今日热点`, `明星推荐`, `热搜人名观察`, `补充观察`, and does not contain removed daily-format sections such as `本周判断` or `数据判断`.

8. Fail closed on rendering or template mismatch.
If the one-step build fails because realtime sources returned zero items, retry the official script after diagnosing network/source access. If HTML was generated but PNG rendering failed, render the same HTML with `scripts/render_observation_png.py`; do not recreate the PNG by drawing with PIL/canvas or by manually rebuilding the design. A hand-made fallback image may be kept only as a temporary diagnostic draft and must not be the primary deliverable unless the user explicitly approves a non-template draft.

## Data Collection

- Prefer existing local project artifacts first. If the workspace has `newsnow`, saved snapshots, or prior observation files, reuse them.
- If current data is needed and local artifacts are stale or missing, browse current primary sources.
- When `ALAPI_TOKEN` is available, treat ALAPI `今日热榜`、`微博热搜榜` and `头条热搜` as the highest-priority real-time inputs, then use other sources to validate sustained heat, risk, and brand fit.
- Treat recency as mandatory. Use the current local date, not a remembered date.
- Prioritize sources in this order:
  1. Real-time channels: Weibo hot search, ALAPI today hot list, ALAPI Toutiao hot search
  2. Work anchors: iQIYI hot list and Tencent Video TV hot search
  3. Maoyan web heat and tracked key-program pages for program-level reinforcement
  4. Douyin and Bilibili as supplemental public-attention and propagation signals
  5. Douban only as reputation correction when needed

## Ranking Model

- Use a two-layer model, not a single blended list.
- First compute `热度发现分` to decide who enters the recommendation pool.
- Then compute `合作判断` using `品牌匹配度` and `风险状态`. These two dimensions must not directly increase the heat ranking.

### Heat Discovery Score

- `内容承接` 40%
- `实时渠道` 30%
- `持续性` 20%
- `多源验证` 10%

When current hot-search signals are unusually strong, use the current-hot-search profile instead of the default profile:

- `内容承接` 32%
- `实时渠道` 38%
- `持续性` 20%
- `多源验证` 10%

Interpretation:

- `内容承接` includes not only in-release film/TV and variety, but also stage moments, comeback topics, classic-work revival, official announcements, and other signals that keep a name from being pure one-off traffic.
- `实时渠道` should currently be split as:
  - Weibo: 15%
  - Toutiao: 8%
  - Aggregated hot-list / news layer: 7%
- In the current-hot-search profile, split `实时渠道` as:
  - Weibo: 20%
  - Toutiao: 10%
  - Aggregated hot-list / news layer: 8%
- `持续性` should reward names that keep appearing across more than one source or keep both content and discussion signals at the same time.
- `多源验证` should reward cross-platform consistency, not any single-platform spike.

Guardrails:

- Do not pre-classify every star as only `影视` or only `综艺` before scoring.
- A person can enter the pool even without a current film/variety release if the real-time discussion is sustained and cross-source.
- A single Weibo hot-search hit must not directly force someone into the top recommendation tier.
- Real-time hot-search stars should still be visible even when they do not enter the top recommendation tier. Add a separate `热搜人名观察` section that distinguishes `正向/可借势` from `负面/需复核` topics.
- Prefer recommending stars who have either clear content anchoring or at least two real-time channels plus follow-through.

Read [references/observation-rules.md](references/observation-rules.md) when you need the detailed content and scoring rules.

## Brand Judgment Rules

- `品牌匹配度` must reflect family, reading, growth, companionship, trust, and parent-friendly recognition.
- `风险状态` must stand alone. Do not let high traffic cancel out controversy.
- `合作建议` must be action-oriented, such as `优先关注`, `可进优先候选`, `先观察`, or `高价值资源位`.
- Do not let `品牌匹配度` or `风险状态` directly raise a person's heat ranking. They belong to the cooperation layer, not the discovery layer.
- Prefer names with content anchoring or sustained cross-source discussion over purely one-off event traffic.
- Do not hide high-current-heat stars just because they lack a work anchor. If the signal is only event-driven or risk-adjacent, list them in the hot-search observation layer instead of the main recommendation layer.
- Always try to resolve works to concrete actor names. Do not leave hot programs unlinked to stars when the cast can be inferred from source fields or local override tables.

## Output Rules

- Keep the hero title as `阿叫热点榜`.
- Keep the hero date formatted as `YYYY.MM.DD`.
- Keep sequence badges in deep red with pure white numbers.
- Keep the date above the title without a box.
- Keep language client-ready. Do not include meta commentary, build notes, or implementation explanations inside the HTML.
- Prefer `明星推荐 10 人` over a shorter star list when the source confidence supports it.
- Include `热搜人名观察` when current hot-search channels surface meaningful celebrity names that are not already in the top recommendation list.
- Put `今日热点` near the top with 4 stacked rank lists: 微博热搜、抖音热搜、B站热搜、影视综艺热榜. Use 10 items per channel when available. Keep the hot-list body text readable around 13px, with enough spacing that the section does not feel crowded.
- Remove long explanatory sections such as `本周判断` and `数据判断` from the daily format unless the user asks for them.
- In `明星推荐`, go straight into the list. Keep the top 4 as full-width cards and let the remaining 6 names use a compact side-by-side layout.
- In `热搜人名观察`, use row-style name entries. Split into `正向/可借势` and `负面/需复核`; use red styling for positive/usable heat and green styling for review-risk heat.
- Simplify `观察名单`、`内容热区`、`影视热区` into short supporting blocks.
- End with a concise brand-summary closing, not a repeated name list. Mention the priority logic: stable work/content support first, event-driven hot search only as borrowing momentum unless risk is resolved.
- Deliver `YYMMDD-阿叫一周娱乐热度观察.png` as the primary output artifact.
- Treat `YYMMDD-阿叫一周娱乐热度观察.html` as the editable source used to render the final image.

## Resources

- Use `scripts/create_daily_observation.py` to create the dated HTML working file from the template.
- Use `scripts/build_daily_observation.py` to fetch current signals, resolve actor names, write the HTML, and optionally render the PNG.
- Use `scripts/render_observation_png.py` to render the HTML into a long PNG image.
- Use `assets/aji-weekly-entertainment-template.html` as the base layout.
- Read `references/observation-rules.md` for the section-by-section writing rules and source priorities.
- Read `references/work_cast_overrides.json` and `references/priority_tracking.json` when you need to improve actor recall for hot programs or strategic stars.
