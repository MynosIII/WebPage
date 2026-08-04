"""Normalize shared metadata and small cross-page conventions.

Run from the repository root with:
    python scripts/normalize_site.py
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://matiasgaglio.onrender.com"
OG_IMAGE = f"{SITE_URL}/og-card.png"
EXCLUDED = {"anchor-test.html", "revolution-test.html", "index.html", "index-es.html", "index-en.html"}


def public_url(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    encoded = "/".join(quote(part) for part in relative.split("/"))
    return f"{SITE_URL}/{encoded}"


def localized_siblings(path: Path) -> tuple[Path | None, Path | None]:
    stem = path.stem
    if stem.endswith("-en") or stem.endswith("-es"):
        base = stem[:-3]
    else:
        base = stem
    english = path.with_name(f"{base}-en.html")
    spanish = path.with_name(f"{base}-es.html")
    return (english if english.exists() else None, spanish if spanish.exists() else None)


def canonical_path(path: Path, language: str) -> Path:
    english, spanish = localized_siblings(path)
    if path.stem.endswith(("-en", "-es")):
        return path
    if language.startswith("es") and spanish:
        return spanish
    if language.startswith("en") and english:
        return english
    return path


def get_attribute(source: str, tag: str, attribute: str) -> str | None:
    match = re.search(rf"<{tag}\b[^>]*\b{attribute}=[\"']([^\"']+)[\"']", source, re.I)
    return html.unescape(match.group(1).strip()) if match else None


def get_meta_description(source: str) -> str | None:
    match = re.search(
        r"<meta\s+[^>]*name=[\"']description[\"'][^>]*content=[\"']([^\"']*)[\"'][^>]*>",
        source,
        re.I,
    )
    if not match:
        match = re.search(
            r"<meta\s+[^>]*content=[\"']([^\"']*)[\"'][^>]*name=[\"']description[\"'][^>]*>",
            source,
            re.I,
        )
    return html.unescape(match.group(1).strip()) if match else None


def encode_attribute_url_spaces(source: str) -> str:
    """Percent-encode spaces in local src/href values without changing their targets."""

    def replace(match: re.Match[str]) -> str:
        prefix, quote_mark, value = match.groups()
        return f"{prefix}{quote_mark}{value.replace(' ', '%20')}{quote_mark}"

    return re.sub(r"(\b(?:src|href)=)([\"'])([^\"']+)\2", replace, source, flags=re.I)


def metadata_block(path: Path, source: str) -> str:
    language = get_attribute(source, "html", "lang") or "es"
    title_match = re.search(r"<title>(.*?)</title>", source, re.I | re.S)
    title = html.unescape(re.sub(r"\s+", " ", title_match.group(1)).strip()) if title_match else "Matías Gaglio"
    description = get_meta_description(source)
    if not description:
        description = (
            "Conversá con Matías Gaglio sobre su trabajo en ecommerce, analítica y creatividad."
            if language.startswith("es")
            else "Talk with Matías Gaglio about his work in ecommerce, analytics, and creative strategy."
        )

    canonical = public_url(canonical_path(path, language))
    english, spanish = localized_siblings(path)
    depth_prefix = "../" * len(path.relative_to(ROOT).parents[:-1])
    locale = "es_AR" if language.startswith("es") else "en_US"
    alternate_locale = "en_US" if locale == "es_AR" else "es_AR"
    image_alt = (
        "Matías Gaglio — portafolio de ecommerce, analítica y estrategia creativa"
        if language.startswith("es")
        else "Matías Gaglio — ecommerce, analytics and creative strategy portfolio"
    )

    lines = [
        "  <!-- Shared discovery metadata: maintained by scripts/normalize_site.py -->",
        f'  <link rel="canonical" href="{canonical}" />',
    ]
    if english and spanish:
        lines.extend(
            [
                f'  <link rel="alternate" hreflang="en" href="{public_url(english)}" />',
                f'  <link rel="alternate" hreflang="es" href="{public_url(spanish)}" />',
                f'  <link rel="alternate" hreflang="x-default" href="{public_url(english)}" />',
            ]
        )
    lines.extend(
        [
            f'  <meta property="og:type" content="website" />',
            f'  <meta property="og:site_name" content="Matías Gaglio" />',
            f'  <meta property="og:locale" content="{locale}" />',
            f'  <meta property="og:locale:alternate" content="{alternate_locale}" />',
            f'  <meta property="og:title" content="{html.escape(title, quote=True)}" />',
            f'  <meta property="og:description" content="{html.escape(description, quote=True)}" />',
            f'  <meta property="og:url" content="{canonical}" />',
            f'  <meta property="og:image" content="{OG_IMAGE}" />',
            f'  <meta property="og:image:width" content="1200" />',
            f'  <meta property="og:image:height" content="630" />',
            f'  <meta property="og:image:alt" content="{image_alt}" />',
            '  <meta name="twitter:card" content="summary_large_image" />',
            f'  <meta name="twitter:title" content="{html.escape(title, quote=True)}" />',
            f'  <meta name="twitter:description" content="{html.escape(description, quote=True)}" />',
            f'  <meta name="twitter:image" content="{OG_IMAGE}" />',
            '  <meta name="referrer" content="strict-origin-when-cross-origin" />',
            '  <meta name="theme-color" content="#121212" />',
            f'  <link rel="icon" href="{depth_prefix}favicon.svg" type="image/svg+xml" />',
            f'  <link rel="manifest" href="{depth_prefix}site.webmanifest" />',
            "  <!-- /Shared discovery metadata -->",
        ]
    )
    return "\n".join(lines)


def normalize(path: Path) -> bool:
    with path.open("r", encoding="utf-8", newline="") as handle:
        source = handle.read()
    if "<head" not in source.lower() or "<body" not in source.lower():
        return False

    managed_metadata = "<!-- Shared discovery metadata:" in source or not re.search(r'<meta\s+[^>]*property=["\']og:', source, re.I)
    updated = source
    if managed_metadata:
        updated = re.sub(
            r"\s*<!-- Shared discovery metadata:.*?<!-- /Shared discovery metadata -->\s*",
            "\n",
            updated,
            flags=re.S,
        )
        updated = re.sub(r"\s*<link\s+[^>]*rel=[\"']canonical[\"'][^>]*>\s*", "\n", updated, flags=re.I)
        updated = re.sub(r"\s*<link\s+[^>]*rel=[\"']alternate[\"'][^>]*>\s*", "\n", updated, flags=re.I)
    updated = re.sub(
        r"\s*<style>\s*\.language-switch\{.*?\.language-switch:focus-visible\{[^}]*}\s*</style>",
        "",
        updated,
        flags=re.S,
    )
    depth_prefix = "../" * len(path.relative_to(ROOT).parents[:-1])
    updated = re.sub(
        r"https://unpkg\.com/aos@(?:next|2\.3\.4)/dist/aos\.css|(?:\.\./)*vendor/aos/aos\.css",
        f"{depth_prefix}vendor/aos/aos.css",
        updated,
    )
    updated = re.sub(
        r"https://unpkg\.com/aos@(?:next|2\.3\.4)/dist/aos\.js|(?:\.\./)*vendor/aos/aos\.js",
        f"{depth_prefix}vendor/aos/aos.js",
        updated,
    )
    updated = re.sub(r"(?<![\w?.])AOS\.init\(", "window.AOS?.init(", updated)
    updated = encode_attribute_url_spaces(updated)
    updated = re.sub(
        r'<li><a href="(?:\.\./)*SEO(?:-en|-es)?\.html">Chat\s*Mat(?:í|i)as</a></li>',
        "",
        updated,
        flags=re.I,
    )
    updated = re.sub(r'(href="(?:\.\./)*consultora-en\.html">)[^<]+', r'\1Opinion Consultancy', updated)
    updated = re.sub(r'(href="(?:\.\./)*sobre-mi-en\.html">)(?:About me|About)', r'\1About', updated)
    updated = re.sub(r'(href="(?:\.\./)*consultora(?:-es)?\.html">)[^<]+', r'\1Investigación de opinión', updated)
    updated = re.sub(r'(href="(?:\.\./)*creatives(?:-es)?\.html">)(?:Creatives|Contenido creativo)', r'\1Contenido creativo', updated)
    updated = updated.replace("&copy; 2025", "&copy; 2026").replace("© 2025", "© 2026")

    if managed_metadata:
        block = metadata_block(path, updated)
        description = re.search(r"<meta\s+[^>]*name=[\"']description[\"'][^>]*>", updated, re.I)
        if description:
            insert_at = description.end()
        else:
            title = re.search(r"</title>", updated, re.I)
            if not title:
                raise ValueError(f"No title insertion point in {path}")
            insert_at = title.end()
        updated = updated[:insert_at] + "\n" + block + updated[insert_at:]

    if updated != source:
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(updated)
        return True
    return False


def main() -> None:
    changed = []
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts or "node_modules" in path.parts or "templates" in path.parts or path.name in EXCLUDED:
            continue
        if normalize(path):
            changed.append(path.relative_to(ROOT).as_posix())
    print(f"Normalized {len(changed)} HTML files.")


if __name__ == "__main__":
    main()
