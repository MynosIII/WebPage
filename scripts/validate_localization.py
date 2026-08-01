"""Validate the bilingual page catalog and reviewed editorial terminology."""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "language-catalog.json"
EXPECTED_PAIRS = 39

# Literal translations and editorial defects found during the bilingual review.
# Keep these strings here so a later bulk edit cannot reintroduce them silently.
BANNED_ES = {
    "Compra Caja": "Use the established Amazon term ‘Buy Box’.",
    "capacidad de descubrimiento": "Use ‘visibilidad en búsquedas’.",
    "unidades abandonadas": "Use ‘inventario varado’.",
    "cargos patrocinados": "Use ‘posiciones patrocinadas’.",
    "Ciencias económicas": "Use ‘Rentabilidad’ in this ecommerce context.",
    "experiencia de cotización": "Use ‘experiencia del listing’.",
    "toma de decisiones del Amazon": "Use ‘toma de decisiones en Amazon’.",
    "más allá de las balas": "Use the established listing term ‘bullets’.",
    "ruido de revisión": "Use ‘ruido de las reseñas’.",
    "escrito defendible": "Use ‘brief defendible’.",
    "seis puertas": "Use ‘seis criterios’.",
    "recolección de palabras clave": "Use ‘keyword harvesting’ or ‘selección de keywords’.",
    "reclamo de recuperación": "Use ‘afirmación de recuperación’.",
    "portfolio ecommerce": "Use ‘portafolio de ecommerce’.",
    "ordered revenue": "Use ‘ingresos por pedidos’.",
    "Medical Sales Representative": "Use the accurate English credential title.",
}

BANNED_EN = {
    "Pulse of the public opinion": "Use ‘Public Opinion Pulse’.",
    "The wear and tear is not only presidential": "Use natural editorial English.",
    "To understand an audience to build a campaign": "Use ‘From understanding … to building …’.",
    "PPC Upscaling": "Use ‘PPC Scaling’.",
    "Sales of Ordered Products": "Use ‘Ordered Product Sales’.",
    "Sales of ordered products": "Use ‘Ordered Product Sales’.",
    "Work lines": "Use ‘Areas of work’.",
    "Are you interested in any?": "Use a natural project CTA.",
}

BAD_ENCODING_FRAGMENTS = ("Ã¡", "Ã©", "Ã­", "Ã³", "Ãº", "Ã±", "â€“", "â€”", "â€™", "ï»¿", "�")


class LocalizedPage(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang = ""
        self.alternates: dict[str, str] = {}
        self.title_parts: list[str] = []
        self.h1_count = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag == "html":
            self.html_lang = values.get("lang", "").lower()
        elif tag == "link" and "alternate" in values.get("rel", "").lower().split() and values.get("hreflang"):
            self.alternates[values["hreflang"].lower()] = values.get("href", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1_count += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())


def contains_bad_control(text: str) -> str | None:
    for char in text:
        if char in {"\n", "\r", "\t"}:
            continue
        if char in {"\u200b", "\u200c", "\u200d", "\ufeff"}:
            return f"invisible character U+{ord(char):04X}"
        category = unicodedata.category(char)
        if category == "Cc":
            return f"control character U+{ord(char):04X}"
    return None


def href_targets(href: str, expected: str) -> bool:
    path = urlsplit(href).path.lstrip("/")
    normalized = expected.replace("\\", "/")
    return path == normalized or (normalized == "index-es.html" and path == "")


def check_file(path: Path, lang: str, expected_es: str, expected_en: str, banned: dict[str, str]) -> list[str]:
    relative = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8")
    parser = LocalizedPage()
    parser.feed(text)
    issues: list[str] = []

    if parser.html_lang != lang:
        issues.append(f"{relative}: expected <html lang=\"{lang}\">, found {parser.html_lang or 'none'}")
    if not parser.title:
        issues.append(f"{relative}: missing localized <title>")
    if parser.h1_count > 1:
        issues.append(f"{relative}: expected at most one H1, found {parser.h1_count}")
    if not href_targets(parser.alternates.get("es", ""), expected_es):
        issues.append(f"{relative}: Spanish hreflang does not target {expected_es}")
    if not href_targets(parser.alternates.get("en", ""), expected_en):
        issues.append(f"{relative}: English hreflang does not target {expected_en}")

    control = contains_bad_control(text)
    if control:
        issues.append(f"{relative}: contains {control}")
    for fragment in BAD_ENCODING_FRAGMENTS:
        if fragment in text:
            issues.append(f"{relative}: contains likely mojibake fragment {fragment!r}")
    for fragment, guidance in banned.items():
        if fragment.casefold() in text.casefold():
            issues.append(f"{relative}: banned translation {fragment!r}. {guidance}")
    return issues


def main() -> int:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["pages"]
    issues: list[str] = []
    if len(catalog) != EXPECTED_PAIRS:
        issues.append(f"language-catalog.json: expected {EXPECTED_PAIRS} bilingual pairs, found {len(catalog)}")

    seen: set[str] = set()
    for entry in catalog:
        page = entry["page"]
        if page in seen:
            issues.append(f"language-catalog.json: duplicate source page {page}")
        seen.add(page)
        es_rel = entry["spanish"]
        en_rel = entry["english"]
        es_path = ROOT / es_rel
        en_path = ROOT / en_rel
        for path in (es_path, en_path):
            if not path.exists():
                issues.append(f"language-catalog.json: missing localized page {path.relative_to(ROOT).as_posix()}")
        if not es_path.exists() or not en_path.exists():
            continue

        # Chat Matías remains a separate workstream; retain structural checks but
        # do not impose this editorial glossary on its unfinished content.
        excluded_editorial = page.startswith("SEO")
        issues.extend(check_file(es_path, "es", es_rel, en_rel, {} if excluded_editorial else BANNED_ES))
        issues.extend(check_file(en_path, "en", es_rel, en_rel, {} if excluded_editorial else BANNED_EN))

        es_title = LocalizedPage()
        es_title.feed(es_path.read_text(encoding="utf-8"))
        en_title = LocalizedPage()
        en_title.feed(en_path.read_text(encoding="utf-8"))
        if es_title.title and en_title.title and es_title.title.casefold() == en_title.title.casefold() and page not in {
            "SEO.html", "index.html", "creatives.html", "ecommerce.html", "amazon-content-architecture.html", "amazon-lifecycle-operating-system.html"
        }:
            issues.append(f"{page}: Spanish and English titles are unexpectedly identical: {es_title.title!r}")

    # Structured bilingual sources must be clean too, even before regeneration.
    for path in sorted((ROOT / "content").glob("*.json")):
        text = path.read_text(encoding="utf-8")
        control = contains_bad_control(text)
        if control:
            issues.append(f"{path.relative_to(ROOT).as_posix()}: contains {control}")
        for fragment in BAD_ENCODING_FRAGMENTS:
            if fragment in text:
                issues.append(f"{path.relative_to(ROOT).as_posix()}: contains likely mojibake fragment {fragment!r}")

    if issues:
        print(f"Localization validation failed with {len(issues)} issue(s):")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"Validated {len(catalog)} bilingual pairs: language declarations, hreflang, encoding and reviewed terminology are clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
