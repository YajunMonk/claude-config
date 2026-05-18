#!/usr/bin/env python
"""Archive the latest Codex-generated images into a date-named project folder."""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
from pathlib import Path


def latest_generation_dir(root: Path) -> Path:
    dirs = [p for p in root.iterdir() if p.is_dir()]
    if not dirs:
        raise SystemExit(f"No generation directories found under {root}")
    return max(dirs, key=lambda p: p.stat().st_mtime)


def image_files(source: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        files.extend(source.glob(pattern))
    return sorted(files, key=lambda p: p.stat().st_mtime)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=r"C:\Users\JOJO\Desktop\AI投流", help="Project folder to archive into.")
    parser.add_argument("--source", help="Specific generated image folder. Defaults to latest under Codex generated_images.")
    parser.add_argument("--generated-root", default=str(Path.home() / ".codex" / "generated_images"))
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="Date folder name, YYYY-MM-DD.")
    parser.add_argument("--scene", default="ad_image", help="Filename scene slug, e.g. parent_child_kitchen.")
    parser.add_argument("--ref", default="ref01", help="Reference id, e.g. ref01 or ref01_round02.")
    parser.add_argument("--count", type=int, default=5, help="How many latest images to copy.")
    args = parser.parse_args()

    project = Path(args.project)
    generated_root = Path(args.generated_root)
    source = Path(args.source) if args.source else latest_generation_dir(generated_root)
    destination = project / args.date
    destination.mkdir(parents=True, exist_ok=True)

    files = image_files(source)
    if not files:
        raise SystemExit(f"No image files found in {source}")

    selected = files[-args.count :]
    copied: list[Path] = []
    for index, file in enumerate(selected, start=1):
        suffix = file.suffix.lower()
        target = destination / f"{args.scene}_{args.ref}_v{index:02d}{suffix}"
        shutil.copy2(file, target)
        copied.append(target)

    for path in copied:
        print(path)


if __name__ == "__main__":
    main()
