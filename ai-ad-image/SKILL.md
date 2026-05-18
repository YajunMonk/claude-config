---
name: ai-ad-image
description: Use only for AI advertising image workflows when the user explicitly asks for ad creatives, paid social ad images, 投流素材, 广告图, 信息流素材, 素材变体, reference-ad-based variants, or 9:16 short-video ad visuals. This skill analyzes reference ad screenshots, ignores watermarks/subtitles/logos/UI/text overlays, creates original 9:16 ad image prompts, generates ad-oriented variants, and archives outputs. Do not use for ordinary image generation, general illustration, profile photos, posters, product photos, or non-ad image editing; use the general imagegen skill instead.
---

# AI 广告图片变体

## Trigger Boundary

Use this skill only when the request includes clear advertising intent, such as:

- 广告图
- 投流素材
- 信息流素材
- ad creative
- paid social creative
- 素材变体
- 参考广告截图生成变体
- 9:16 短视频广告封面或广告画面

Do not use this skill for:

- 普通图片生成
- 头像、插画、海报、封面
- 单张概念图
- 产品图
- 图片修图或换背景
- 非广告用途的亲子、家庭、教育图片

If the user only says "生成图片" or "参考这张图生成图片" without ad intent, use the general `imagegen` skill.

## Core Rule

Create original ad images that borrow only high-level creative direction from references: composition, camera language, lighting, mood, scene type, and commercial texture. Do not remove watermarks, reconstruct covered image regions, copy exact faces, copy exact outfits, copy logos, copy subtitles, copy platform UI, or recreate a competitor creative one-for-one.

Always generate `9:16` vertical images unless the user explicitly changes the ratio.

## Workflow

1. Inspect the reference image.
   - Identify subject hierarchy, camera angle, crop, foreground/background placement, lighting, color palette, emotional hook, scene category, props, and ad-like texture.
   - Treat watermarks, subtitles, corner badges, UI overlays, logos, brand packaging, and readable text as noise.
   - If the reference contains children, keep the new result family-safe, natural, and non-sexualized.

2. Write a clean source prompt before generation.
   - Describe only reusable visual attributes.
   - Explicitly require different people, different clothing, and a different background.
   - Include negative constraints: no text, no subtitles, no watermark, no logo, no UI overlay, no copied identities, no branded packaging.
   - Use `references/prompt-template.md` when a structured prompt is useful.

3. Generate 5 variants.
   - Variant 1: closest legal high-level match to the reference composition.
   - Variant 2: change expression/interaction while preserving the main scene.
   - Variant 3: change family member pairing or child age/gender when appropriate.
   - Variant 4: change background, props, or home environment.
   - Variant 5: stronger commercial polish or more natural candid realism, depending on user goal.
   - Use the image generation tool directly. Do not ask for confirmation unless the input is missing.

4. Save outputs.
   - Copy generated images out of Codex's default generated image directory into the user's project folder.
   - Create a date folder named `YYYY-MM-DD`, using the current local date.
   - Use descriptive filenames: `<scene>_refNN_v01.png` through `<scene>_refNN_v05.png`.
   - Keep original generated files in place.
   - Use `scripts/archive_generated_images.py` for repeatable copy/rename work.

5. Iterate from feedback.
   - Preserve the best selected attributes from the user's feedback.
   - Generate another batch of 5 unless the user asks for a different count.
   - Save each batch with a new reference or round marker, for example `ref01_round02_v01.png`.

## Output Notes

When reporting results, include:

- The destination folder path.
- The 5 saved filenames.
- A short note that images are 9:16 vertical, or mention if the generator returned a near-9:16 size.

## Prompting Guidelines

Prefer concrete visual language over generic style words. Good prompt sections:

- Scene and subjects
- Composition and camera
- Interaction/emotion
- Lighting/color/texture
- Originality constraints
- Negative text/logo/watermark constraints

For Chinese advertising workflows, prompts may be drafted in Chinese first, then converted into English for image generation if that gives more stable visual results.

## Resources

- `references/prompt-template.md`: reusable prompt structure and examples for parent-child/kitchen/education ad imagery.
- `scripts/archive_generated_images.py`: copy and rename the latest generated images into a date-named project folder.
