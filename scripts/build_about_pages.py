"""Build the bilingual professional-story pages."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from string import Template

from shared_nav import render_global_nav

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "about.json"
TEMPLATE = ROOT / "templates" / "about.html"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render(data: dict[str, object], default: bool = False) -> str:
    lang = str(data["lang"])
    es = lang == "es"
    nav = (
        [("Inicio", "index.html"), ("Casos", "index.html#casos"), ("Sobre mí", "sobre-mi-es.html"), ("CV", "output/pdf/Matias-Gaglio-CV-ES.pdf"), ("Contacto", "#contacto")]
        if es
        else [("Home", "index-en.html"), ("Case Studies", "index-en.html#cases"), ("About", "sobre-mi-en.html"), ("Resume", "output/pdf/Matias-Gaglio-Resume-EN.pdf"), ("Contact", "#contact")]
    )
    nav_items = "".join(f'<li><a href="{esc(href)}">{esc(label)}</a></li>' for label, href in nav)
    chapters = "".join(
        f'<article class="story-chapter"><span>{esc(index)}</span><h3>{esc(title)}</h3><p>{esc(copy)}</p></article>'
        for index, title, copy in data["chapters"]
    )
    facts_data = [(data["role_label"], data["role"]), (data["focus_label"], data["focus"]), (data["education_label"], data["education"])]
    facts = "".join(
        f'<div class="about-profile-fact"><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>'
        for label, value in facts_data
    )
    tools = "".join(f"<li>{esc(item)}</li>" for item in data["tools"])
    slug = "sobre-mi" if default else f"sobre-mi-{lang}"
    values = {
        "global_nav": render_global_nav(lang, "sobre-mi-en.html" if es else "sobre-mi-es.html"),
        **{key: esc(value) for key, value in data.items() if not isinstance(value, list)},
        "canonical": f"https://matiasgaglio.onrender.com/{slug}.html",
        "skip_label": "Saltar al contenido principal" if es else "Skip to main content",
        "home_href": "index.html" if es else "index-en.html",
        "home_label": "Inicio" if es else "Home",
        "nav_label": "Navegación principal" if es else "Primary navigation",
        "nav_items": nav_items,
        "contact_label": "Hablemos" if es else "Contact me",
        "switch_href": "sobre-mi-en.html" if es else "sobre-mi-es.html",
        "switch_lang": "en" if es else "es",
        "switch_aria": "View in English" if es else "Ver en español",
        "switch_label": "EN" if es else "ES",
        "menu_open": "Abrir menú" if es else "Open menu",
        "menu_close": "Cerrar menú" if es else "Close menu",
        "story_label": "Historia profesional" if es else "Professional story",
        "profile_label": "Perfil profesional" if es else "Professional profile",
        "chapters": chapters,
        "facts": facts,
        "tools": tools,
        "contact_id": "contacto" if es else "contact",
        "next_label": "Próximo paso" if es else "Next step",
    }
    return Template(TEMPLATE.read_text(encoding="utf-8")).substitute(values).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    expected = {
        ROOT / "sobre-mi-es.html": render(data["es"]),
        ROOT / "sobre-mi-en.html": render(data["en"]),
        ROOT / "sobre-mi.html": render(data["es"], default=True),
    }
    stale = []
    for path, content in expected.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path.name)
        else:
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"Built {path.name}")
    if stale:
        print("Stale generated About pages: " + ", ".join(stale))
        return 1
    if args.check:
        print("Generated About pages are current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
