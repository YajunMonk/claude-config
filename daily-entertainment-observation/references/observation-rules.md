# Daily Entertainment Observation Rules

## 1. Default Output

- Primary output file: `YYMMDD-阿叫一周娱乐热度观察.png`
- Working source file: `YYMMDD-阿叫一周娱乐热度观察.html`
- Default to generating a new date-prefixed HTML/PNG pair instead of updating an old report in place.
- If the same-day default filename already exists, auto-create a suffixed pair such as `YYMMDD-阿叫一周娱乐热度观察-02.html` and `.png`.
- Use date format `YYYY.MM.DD`.
- Prefer a mobile-first long image that reads clearly on phones and tablets.
- Cut low-value detail aggressively. Keep only the content a brand teammate can act on quickly.
- Default to `推荐 10 人` instead of a shorter list when the data supports it.

## 2. Voice and Tone

- Write for internal brand decision-making, not for production handoff.
- Keep language direct, clean, and brief.
- Remove process words such as:
  - `本版`
  - `样式稿`
  - `说明`
  - `口径`
  - `免费方案`
  - `当前版本`
  - `内部分享用`

## 3. Section Rules

### Hero

- Keep department label as `叫叫品牌营销中心`.
- Keep the date above the title.
- Keep the title as `阿叫热点榜`.
- Keep the supporting text short and brand-decision oriented: explain that the report filters usable attention from full-network hot topics, short-video spread, community discussion, and film/variety heat, then prioritizes stars that can support parent-growth, family-companionship, and brand-trust narratives.

### Hot Stars Top 10

- Place `今日热点` before the recommendation section with 4 stacked rank lists: 微博热搜、抖音热搜、B站热搜、影视综艺热榜.
- Use 10 items per rank list when available. Keep typography readable and spacious; do not squeeze this section into a 2x2 grid.
- Prefer a short priority list over a dense table when readability improves.
- Keep badge numbers centered.
- Keep badge background deep red and badge numbers pure white.
- Prefer stars with clear content anchoring or sustained cross-source discussion over pure one-off controversy traffic.
- In `明星推荐`, keep the top 4 as full-width cards. Use compact side-by-side cards for the remaining 6. One short reason line plus three judgment pills is usually enough.
- Extract actor names from work-level signals whenever possible. If a source only gives a program title, try local work-to-cast overrides before giving up.

### Hot-Search Name Observation

- Use `热搜人名观察` for celebrity names surfaced by current hot search but not promoted into main recommendations.
- Render as row-style entries instead of large stacked cards.
- Split `正向/可借势` and `负面/需复核`.
- Use red styling for positive/usable heat and green styling for review-risk heat.
- Keep copy short: source, topic, and next action such as `可借势，继续看承接` or `先复核口碑与后续发酵`.

### Variety

- Keep the section to a small number of cards.
- Use short descriptors such as `综艺回归`, `舞台讨论`, `爱奇艺热播`, `稳定讨论`.

### Film and TV

- Use iQIYI and Tencent Video as the main anchors.
- Keep Douban as supporting tone and reputation context, not the main heat score.

### Data Source Judgment

- Do not include a separate `数据判断` section in the daily format unless the user explicitly asks for one.

## 4. Ranking Model

Use a two-layer model:

1. `热度发现分`: decide who enters the main recommendation pool
2. `合作判断`: use `品牌匹配度` and `风险状态` to decide whether the person is `优先关注`、`可进优先候选` or `先观察`

### 4.1 Heat Discovery Score

- `内容承接` 40%
- `实时渠道` 30%
- `持续性` 20%
- `多源验证` 10%

Use the current-hot-search profile when Weibo / Toutiao / 今日热榜 have several high-rank celebrity topics:

- `内容承接` 32%
- `实时渠道` 38%
- `持续性` 20%
- `多源验证` 10%

Detailed interpretation:

- `内容承接` includes film/TV, variety, stage/music moments, official return signals, classic-work revival, and other non-one-off anchors.
- `实时渠道` should currently be split as Weibo 15%, Toutiao 8%, aggregated hot-list / news layer 7%.
- Under the current-hot-search profile, split `实时渠道` as Weibo 20%, Toutiao 10%, aggregated hot-list / news layer 8%.
- `持续性` should reward names that keep appearing across more than one source or that have both content and discussion carrying the heat forward.
- `多源验证` should reward cross-platform consistency, not a single spike.

Guardrails:

- Do not pre-filter people into only `影视` or only `综艺` before scoring.
- A single Weibo hot-search hit should not directly create a top recommendation.
- A single Weibo hot-search hit should still be visible when celebrity relevance is clear; place it in `热搜人名观察`, not necessarily in the main recommendation list.
- A person without a current film/variety release can still enter the pool if the discussion is sustained and multi-source.
- `品牌匹配度` and `风险状态` should never directly raise the discovery ranking.

### 4.2 Real-Time Hot-Search Observation

- Add a separate `热搜人名观察` section when hot-search topics surface stars outside the main list.
- Split the section into `正向/可借势` and `负面/需复核`.
- Treat concerts, stage moments, comeback topics, official announcements, public praise, and high-engagement variety clips as positive or usable momentum.
- Treat allegations, fan loss, controversy, apology, relationship conflict, legal/ethical issues, or unclear accusations as `需复核`.
- Do not let negative heat enter the main recommendation tier until the risk is resolved.

## 5. Source Priority

1. Weibo hot search / ALAPI today hot list / ALAPI Toutiao hot search: build the first-pass real-time candidate pool
2. Weibo entertainment: star events, variety breakout moments, and risk review
3. iQIYI: variety and drama work heat
4. Tencent Video: drama and actor heat
5. Maoyan web heat / tracked key-program pages: reinforce program-level signal and reduce misses
6. Bilibili hot video / hot search: youth-side propagation
7. Douyin: supplemental public attention
8. Douban: tone and reputation correction

## 6. Brand Fit Heuristics

### High Match

- Warm, steady, credible
- Compatible with family, reading, growth, companionship
- Recognizable to young parents or family audiences
- Recent work window or stable positive visibility

### Mid Match

- Broad awareness but weaker direct connection to reading/growth
- Suitable for topic-led or lighter campaigns

### Watch / Lower Match

- Attention comes mostly from controversy or unstable event traffic
- Hard to connect naturally to family or reading themes

## 7. Risk Heuristics

- `低风险`: no strong current controversy signal
- `需复核`: event-driven discussion, unclear follow-up, or mixed public signal
- Use stronger warnings only when current primary-source evidence supports it

## 8. Collaboration Suggestion Patterns

- `优先关注`
- `可进优先候选`
- `值得推进`
- `可做主题型合作`
- `先观察，不进优先候选`
- `高价值资源位`

## 9. Final Summary

- End with one concise brand judgment.
- Summarize who to prioritize and why.
- State that event-driven hot search is borrowing momentum unless there is stable work/content support and low risk.
