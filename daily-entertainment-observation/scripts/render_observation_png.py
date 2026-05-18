#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def derive_output_path(html_path: Path, explicit_output: str | None) -> Path:
    if explicit_output:
        return Path(explicit_output).expanduser().resolve()
    return html_path.with_suffix(".png")


def validate_rendered_png(output_path: Path, min_width: int, min_height: int, min_bytes: int) -> bool:
    if not output_path.exists():
        print(f"PNG output was not created: {output_path}", file=sys.stderr)
        return False
    if output_path.stat().st_size < min_bytes:
        print(
            f"PNG output is too small for the original long template: "
            f"{output_path.stat().st_size} bytes < {min_bytes} bytes",
            file=sys.stderr,
        )
        return False
    try:
        from PIL import Image
    except ImportError:
        return True
    try:
        with Image.open(output_path) as image:
            width, height = image.size
    except Exception as exc:
        print(f"Could not inspect PNG dimensions: {exc}", file=sys.stderr)
        return False
    if width < min_width or height < min_height:
        print(
            f"PNG dimensions do not match the original long template: "
            f"{width}x{height}, expected at least {min_width}x{min_height}",
            file=sys.stderr,
        )
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the entertainment observation HTML into a long PNG image.")
    parser.add_argument("--html", required=True, help="Path to the HTML working file.")
    parser.add_argument("--output-file", default=None, help="Optional PNG output path. Defaults to the HTML stem with .png.")
    parser.add_argument("--device", default="Pixel 7", help="Playwright device preset to use for the screenshot.")
    parser.add_argument("--min-width", type=int, default=1000, help="Minimum acceptable PNG width for template QA.")
    parser.add_argument("--min-height", type=int, default=8000, help="Minimum acceptable PNG height for template QA.")
    parser.add_argument("--min-bytes", type=int, default=1500000, help="Minimum acceptable PNG file size for template QA.")
    args = parser.parse_args()

    html_path = Path(args.html).expanduser().resolve()
    if not html_path.exists():
        print(f"HTML file not found: {html_path}", file=sys.stderr)
        return 1

    npx = shutil.which("npx")
    if not npx:
        print("npx not found in PATH. Install Node.js to render the PNG.", file=sys.stderr)
        return 1

    output_path = derive_output_path(html_path, args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        npx,
        "playwright",
        "screenshot",
        f"--device={args.device}",
        "--full-page",
        html_path.as_uri(),
        str(output_path),
    ]

    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        if "Executable doesn't exist" in stderr or "playwright install" in stderr:
            stderr += "\nRun `npx playwright install chromium` once, then try again."
        print(stderr or "Failed to render PNG.", file=sys.stderr)
        return completed.returncode

    if not validate_rendered_png(output_path, args.min_width, args.min_height, args.min_bytes):
        return 1

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
