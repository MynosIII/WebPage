"""Add intrinsic dimensions to local raster images without reformatting HTML."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
IMAGE_TAG = re.compile(r"<img\b[^>]*>", re.I | re.S)
SRC = re.compile(r"\bsrc\s*=\s*([\"'])(.*?)\1", re.I | re.S)


def dimensions(path: Path) -> tuple[int, int] | None:
    try:
        with Image.open(path) as image:
            return image.size
    except (OSError, ValueError):
        return None


def update_page(path: Path) -> tuple[str, int]:
    source = path.read_text(encoding="utf-8")
    changed = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal changed
        tag = match.group(0)
        has_width = re.search(r"\bwidth\s*=", tag, re.I)
        has_height = re.search(r"\bheight\s*=", tag, re.I)
        if has_width and has_height:
            return tag
        src_match = SRC.search(tag)
        if not src_match:
            return tag
        parsed = urlsplit(src_match.group(2))
        if parsed.scheme or parsed.netloc or not parsed.path:
            return tag
        target = (path.parent / unquote(parsed.path)).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            return tag
        size = dimensions(target)
        if not size:
            return tag
        additions = ""
        if not has_width:
            additions += f' width="{size[0]}"'
        if not has_height:
            additions += f' height="{size[1]}"'
        if not re.search(r"\bdecoding\s*=", tag, re.I):
            additions += ' decoding="async"'
        changed += 1
        return re.sub(r"\s*/?>$", lambda end: f"{additions}{' />' if '/' in end.group(0) else '>'}", tag)

    return IMAGE_TAG.sub(replace, source), changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Report pages still missing resolvable dimensions.")
    args = parser.parse_args()
    total = 0
    affected: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        updated, changed = update_page(path)
        if not changed:
            continue
        total += changed
        affected.append(path.relative_to(ROOT).as_posix())
        if not args.check:
            path.write_text(updated, encoding="utf-8", newline="")
    if args.check and total:
        print(f"{total} local image(s) still need dimensions across {len(affected)} page(s).")
        return 1
    verb = "Would update" if args.check else "Updated"
    print(f"{verb} {total} image(s) across {len(affected)} page(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
