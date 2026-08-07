"""Add tools mentioned in case HTML to the shared case-tool lookup."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "content" / "case-tools.json"
PUBLIC_DIRS = (ROOT, ROOT / "Cases")


def base_page_name(name: str) -> str:
    return re.sub(r"-(?:en|es)(?=\.html$)", "", name, flags=re.I).lower()


def public_case_sources() -> dict[str, str]:
    sources: dict[str, list[str]] = {}
    for directory in PUBLIC_DIRS:
        for path in directory.glob("*.html"):
            key = base_page_name(path.name)
            sources.setdefault(key, []).append(path.read_text(encoding="utf-8"))
    return {key: html.unescape("\n".join(parts)) for key, parts in sources.items()}


def mentions(source: str, alias: str) -> bool:
    escaped = re.escape(alias).replace(r"\ ", r"\s+")
    return re.search(rf"(?<![\w]){escaped}(?![\w])", source, flags=re.I) is not None


def synchronized_cases(catalog: dict, sources: dict[str, str]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    tools = catalog.get("tools", {})
    current_cases = catalog.get("cases", {})
    updated: dict[str, list[str]] = {}
    additions: dict[str, list[str]] = {}

    for page_name, declared_stack in current_cases.items():
        stack = list(dict.fromkeys(declared_stack))
        source = sources.get(page_name.lower(), "")
        found = [
            tool_id
            for tool_id, tool in tools.items()
            if any(mentions(source, alias) for alias in tool.get("aliases", []))
        ]
        missing = [tool_id for tool_id in found if tool_id not in stack]
        if missing:
            additions[page_name] = missing
            stack.extend(missing)
        updated[page_name] = stack

    return updated, additions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail when mentioned tools are absent from the lookup.")
    args = parser.parse_args()

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    updated_cases, additions = synchronized_cases(catalog, public_case_sources())
    if not additions:
        print("Case tool lookup is current.")
        return 0

    summary = "; ".join(f"{page}: {', '.join(tool_ids)}" for page, tool_ids in additions.items())
    if args.check:
        print(f"Case tool lookup is missing mentioned tools: {summary}")
        return 1

    catalog["cases"] = updated_cases
    CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Updated case tool lookup: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
