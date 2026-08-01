"""Generate robots.txt and sitemap.xml from canonical HTML metadata."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://matiasgaglio.onrender.com"
EXCLUDED = {"404.html", "anchor-test.html", "revolution-test.html"}


def canonical_url(source: str) -> str | None:
    match = re.search(
        r'<link\b(?=[^>]*\brel=["\']canonical["\'])(?=[^>]*\bhref=["\']([^"\']+)["\'])[^>]*>',
        source,
        re.I,
    )
    return html.unescape(match.group(1)) if match else None


def build_outputs() -> dict[Path, str]:
    urls: set[str] = {f"{SITE_URL}/"}
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts or path.name in EXCLUDED:
            continue
        source = path.read_text(encoding="utf-8")
        if re.search(r'<meta\b[^>]*\bname=["\']robots["\'][^>]*\bcontent=["\'][^"\']*noindex', source, re.I):
            continue
        canonical = canonical_url(source)
        if canonical and canonical.startswith(f"{SITE_URL}/"):
            urls.add(canonical)

    sitemap = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    sitemap.extend(f"  <url><loc>{html.escape(url)}</loc></url>" for url in sorted(urls))
    sitemap.append("</urlset>")
    robots = "\n".join([
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: {SITE_URL}/sitemap.xml",
        "",
    ])
    return {
        ROOT / "sitemap.xml": "\n".join(sitemap) + "\n",
        ROOT / "robots.txt": robots,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if generated files are stale.")
    args = parser.parse_args()
    stale: list[str] = []
    for path, expected in build_outputs().items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                stale.append(path.name)
        else:
            path.write_text(expected, encoding="utf-8", newline="\n")
            print(f"Built {path.name}")
    if stale:
        print(f"Generated discovery files are stale: {', '.join(stale)}")
        return 1
    if args.check:
        print("robots.txt and sitemap.xml are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
