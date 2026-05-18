# AI 投流图片提示词模板

## Clean Prompt Template

```text
Generate an original 9:16 vertical realistic advertising-style image.

Reference abstraction:
- Scene type: [home kitchen / study desk / classroom / living room / outdoor parent-child activity]
- Subjects: [parent + child relationship, approximate age, posture, gaze, interaction]
- Composition: [medium shot / close-up / slight high angle / subject center / child lower-left / prop lower-center]
- Lighting: [soft daylight / warm indoor light / clean commercial light]
- Texture: [realistic smartphone ad still / polished commercial photo / lightly stylized but believable]
- Mood: [warm, focused, trusting, educational, candid]
- Props: [bowl, book, tablet, toy, worksheet, learning materials]

Originality requirements:
- Use different faces, different clothing, and a different background from the reference.
- Preserve only high-level composition, camera language, lighting mood, and ad texture.

Negative constraints:
- No text, no Chinese characters, no subtitles, no watermark, no logo, no UI overlay.
- No brand marks, no readable packaging, no exact copied face, no exact copied outfit.
- No distorted hands, no extra fingers, no unnatural child anatomy.
```

## Parent-Child Kitchen Example

```text
Generate an original 9:16 vertical realistic advertising-style image of a young parent and a school-age child doing a simple baking activity in a bright modern home kitchen. The parent is the central subject, gently whisking batter in a stainless mixing bowl at the countertop, while the child stands close beside them watching with curiosity and focus. Medium shot, slight high angle, vertical short-video screenshot framing, bowl and hands visible in the lower center, parent upper center, child near the lower side. Soft natural daylight, clean grey-white kitchen, warm family education mood, candid but polished commercial texture.

Use different faces, different clothing, and a different kitchen layout from any reference image. Do not include text, subtitles, watermark, logo, UI overlay, brand packaging, copied identities, or readable labels. Keep hands realistic and the scene natural.
```

## Variant Directions

1. Closest composition: keep subject placement and camera angle close, but change identities, clothing, and room.
2. Interaction change: parent guides the child's hand, child participates more actively.
3. Pairing change: mother-son, mother-daughter, father-son, father-daughter, grandparent-child if useful.
4. Environment change: different kitchen color, counter material, window placement, props.
5. Ad polish change: more candid realism or more polished commercial lighting.

## Naming Pattern

Use concise English filenames for cross-tool compatibility:

```text
parent_child_kitchen_ref01_v01.png
parent_child_kitchen_ref01_v02.png
parent_child_kitchen_ref01_v03.png
parent_child_kitchen_ref01_v04.png
parent_child_kitchen_ref01_v05.png
```
