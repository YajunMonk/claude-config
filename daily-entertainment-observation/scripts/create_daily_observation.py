#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path


DEFAULT_BASENAME = "阿叫一周娱乐热度观察"
DATE_PLACEHOLDER = "{{OBSERVATION_DATE}}"
DATE_PATTERN = re.compile(r"\b\d{4}\.\d{2}\.\d{2}\b")


def resolve_template_path() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "aji-weekly-entertainment-template.html"


def normalize_date(raw: str | None) -> str:
    if not raw:
        return date.today().strftime("%Y.%m.%d")

    for fmt in ("%Y.%m.%d", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y.%m.%d")
        except ValueError:
            continue

    raise ValueError(f"Unsupported date format: {raw}")


def build_default_output_file(formatted_date: str) -> str:
    date_prefix = datetime.strptime(formatted_date, "%Y.%m.%d").strftime("%y%m%d")
    return f"{date_prefix}-{DEFAULT_BASENAME}.html"


def pick_available_output_path(output_dir: Path, formatted_date: str) -> Path:
    base_name = build_default_output_file(formatted_date)
    candidate = output_dir / base_name
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    counter = 2
    while True:
        numbered = output_dir / f"{stem}-{counter:02d}{suffix}"
        if not numbered.exists():
            return numbered
        counter += 1


def render_template(template_text: str, formatted_date: str) -> str:
    if DATE_PLACEHOLDER in template_text:
        return template_text.replace(DATE_PLACEHOLDER, formatted_date)

    return DATE_PATTERN.sub(formatted_date, template_text, count=1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create today's entertainment observation HTML from the skill template.")
    parser.add_argument("--output-dir", default=".", help="Directory for the generated HTML file.")
    parser.add_argument("--output-file", default=None, help="Output HTML filename. Defaults to YYMMDD-prefixed report name.")
    parser.add_argument("--date", dest="raw_date", default=None, help="Date in YYYY.MM.DD, YYYY-MM-DD, or YYYY/MM/DD.")
    parser.add_argument("--force", action="store_true", help="Overwrite the output file if it already exists.")
    args = parser.parse_args()

    template_path = resolve_template_path()
    if not template_path.exists():
        print(f"Template not found: {template_path}", file=sys.stderr)
        return 1

    try:
        formatted_date = normalize_date(args.raw_date)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / args.output_file if args.output_file else pick_available_output_path(output_dir, formatted_date)

    if output_path.exists() and not args.force:
        print(f"Output already exists: {output_path}", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        return 1

    template_text = template_path.read_text(encoding="utf-8")
    rendered = render_template(template_text, formatted_date)
    output_path.write_text(rendered, encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
