"""Fail fast on broken static-site references and deployment hygiene regressions."""

from __future__ import annotations

import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
TEST_STUBS = {"anchor-test.html", "revolution-test.html"}
FORBIDDEN_SUFFIXES = {".doc", ".docx", ".xls", ".xlsx", ".download"}
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}
LOCAL_ONLY_DIRS = {".git", "node_modules", "tmp"}


def is_deploy_source(path: Path) -> bool:
    return not any(part in LOCAL_ONLY_DIRS for part in path.relative_to(ROOT).parts)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.references: list[tuple[str, str]] = []
        self.images_without_alt = 0
        self.meta_names: set[str] = set()
        self.meta_properties: set[str] = set()
        self.link_rels: list[tuple[set[str], dict[str, str]]] = []
        self.has_structured_data = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.append(values["id"])
        if tag in {"a", "link"} and values.get("href"):
            self.references.append(("href", values["href"]))
        if tag in {"img", "script", "source", "video"} and values.get("src"):
            self.references.append(("src", values["src"]))
        if tag == "img" and "alt" not in values:
            self.images_without_alt += 1
        if tag == "meta":
            if values.get("name"):
                self.meta_names.add(values["name"].lower())
            if values.get("property"):
                self.meta_properties.add(values["property"].lower())
        if tag == "link":
            self.link_rels.append((set(values.get("rel", "").lower().split()), values))
        if tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self.has_structured_data = True


def exact_case_path(path: Path) -> bool:
    try:
        relative = path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return False
    current = ROOT
    for part in relative.parts:
        if not current.is_dir():
            return False
        names = {child.name for child in current.iterdir()}
        if part not in names:
            return False
        current /= part
    return current.exists()


def parser_for(path: Path, cache: dict[Path, PageParser]) -> PageParser:
    path = path.resolve()
    if path not in cache:
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8"))
        cache[path] = parser
    return cache[path]


def validate_page(path: Path, cache: dict[Path, PageParser]) -> list[str]:
    issues: list[str] = []
    parser = parser_for(path, cache)
    relative = path.relative_to(ROOT).as_posix()

    duplicates = [value for value, count in Counter(parser.ids).items() if count > 1]
    if duplicates:
        issues.append(f"{relative}: duplicate ids: {', '.join(duplicates)}")
    if parser.images_without_alt:
        issues.append(f"{relative}: {parser.images_without_alt} image(s) missing alt attributes")

    special = path.name == "404.html"
    if not special:
        required_meta = {"twitter:card", "referrer"}
        if not path.stem.lower().startswith("seo"):
            required_meta.add("description")
        for item in sorted(required_meta - parser.meta_names):
            issues.append(f"{relative}: missing meta name={item}")
        for item in sorted({"og:title", "og:description", "og:url", "og:image"} - parser.meta_properties):
            issues.append(f"{relative}: missing meta property={item}")
        rel_sets = [rels for rels, _ in parser.link_rels]
        for item in {"canonical", "icon", "manifest"}:
            if not any(item in rels for rels in rel_sets):
                issues.append(f"{relative}: missing link rel={item}")

    if path.name in {"index.html", "index-es.html", "index-en.html"} and not parser.has_structured_data:
        issues.append(f"{relative}: missing JSON-LD structured data")

    if path.stem.lower().endswith("-es"):
        source = path.read_text(encoding="utf-8")
        main_match = re.search(r"<main\b.*?</main>", source, re.I | re.S)
        if main_match:
            plain = re.sub(r"<[^>]+>", " ", main_match.group()).lower()
            words = re.findall(r"[a-záéíóúñü]+", plain)
            english = sum(word in {"the", "and", "with", "from", "this", "that", "before", "after", "should", "when", "into", "which", "while", "each", "source", "customer", "listing", "search"} for word in words)
            spanish = sum(word in {"el", "la", "los", "las", "una", "un", "con", "desde", "este", "esta", "que", "antes", "después", "cuando", "para", "cada", "fuente", "cliente", "búsqueda"} for word in words)
            if english >= 40 and english > spanish:
                issues.append(f"{relative}: Spanish page appears predominantly English ({english} English signals vs {spanish} Spanish signals)")

    local_ids = set(parser.ids)
    if path.stem.lower().startswith("unimac-case"):
        rationale = ROOT / "creatives" / "flyers" / "unimac-heater" / "design-rationale.txt"
        blocks = [block.strip() for block in re.split(r"\n\s*\n", rationale.read_text(encoding="utf-8").replace("\r", ""))]
        local_ids.update(
            re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", re.sub(r"^\d+\.\s*", "", block).lower()))
            for block in blocks
            if len(block) < 90 and block == block.upper() and re.search(r"[A-Z]", block)
        )
    for attribute, raw in parser.references:
        if not raw or raw.startswith("//") or "${" in raw:
            continue
        parsed = urlsplit(raw)
        if parsed.scheme.lower() in SKIP_SCHEMES:
            continue
        if not parsed.path:
            target = path
        else:
            target = (path.parent / unquote(parsed.path)).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            issues.append(f"{relative}: {attribute} escapes repository: {raw}")
            continue
        if not target.exists():
            issues.append(f"{relative}: missing local target: {raw}")
            continue
        if not exact_case_path(target):
            issues.append(f"{relative}: filename casing mismatch: {raw}")
            continue
        if parsed.fragment and target.suffix.lower() in {".html", ".htm"}:
            target_ids = local_ids if target.resolve() == path.resolve() else set(parser_for(target, cache).ids)
            if unquote(parsed.fragment) not in target_ids:
                issues.append(f"{relative}: missing anchor target: {raw}")
        elif parsed.fragment and not parsed.path and unquote(parsed.fragment) not in local_ids:
            issues.append(f"{relative}: missing anchor target: {raw}")
    return issues


def main() -> int:
    issues: list[str] = []
    cache: dict[Path, PageParser] = {}
    pages = [
        path
        for path in ROOT.rglob("*.html")
        if is_deploy_source(path) and "templates" not in path.parts and path.name not in TEST_STUBS
    ]
    for path in sorted(pages):
        issues.extend(validate_page(path, cache))

    forbidden = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and is_deploy_source(path) and path.suffix.lower() in FORBIDDEN_SUFFIXES
    ]
    if forbidden:
        issues.append("Forbidden deploy-source files:\n  " + "\n  ".join(sorted(forbidden)))

    if re.search(r"(?<!window\.)AOS\.init\(", "\n".join(path.read_text(encoding="utf-8") for path in pages)):
        issues.append("Unprotected AOS.init() call found; use window.AOS?.init().")

    for generated in (ROOT / "robots.txt", ROOT / "sitemap.xml"):
        if not generated.exists():
            issues.append(f"Missing generated discovery file: {generated.name}")

    if issues:
        print(f"Validation failed with {len(issues)} issue(s):")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"Validated {len(pages)} HTML pages: references, anchors, casing, metadata and deploy hygiene are clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
