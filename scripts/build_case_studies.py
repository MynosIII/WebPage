"""Build standardized bilingual case studies from shared narratives and verified claims."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from string import Template
from urllib.parse import quote

from shared_nav import render_global_nav


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "case-studies.json"
CLAIMS = ROOT / "content" / "project-claims.json"
TEMPLATE = ROOT / "templates" / "case-study.html"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_nav(lang: str) -> str:
    items = (
        [("Inicio", "index.html"), ("Casos", "index.html#casos"), ("Sobre mí", "sobre-mi-es.html"), ("CV", "output/pdf/Matias-Gaglio-CV-ES.pdf"), ("Contacto", "mailto:matiasignaciogaglio@gmail.com")]
        if lang == "es"
        else [("Home", "index-en.html"), ("Case Studies", "index-en.html#cases"), ("About", "sobre-mi-en.html"), ("Resume", "output/pdf/Matias-Gaglio-Resume-EN.pdf"), ("Contact", "mailto:matiasignaciogaglio@gmail.com")]
    )
    return "".join(f'<li><a href="{esc(href)}">{esc(label)}</a></li>' for label, href in items)


def render_actions(items: list[list[str]]) -> str:
    return "".join(
        f'<article class="action-card"><span>{index:02d}</span><h3>{esc(title)}</h3><p>{esc(copy)}</p></article>'
        for index, (title, copy) in enumerate(items, start=1)
    )


def render_results(claim: dict[str, object], lang: str) -> str:
    return "".join(
        f'<div class="result-card"><strong>{esc(item.split(" ", 1)[0])}</strong><span>{esc(item.split(" ", 1)[1] if " " in item else "")}</span></div>'
        for item in claim["approved_public_claims"][lang]
    )


def render_visuals(case: dict[str, object], lang: str) -> str:
    figures = []
    for src, width, height, _shared_alt, caption_es, caption_en in case.get("visuals", []):
        caption = caption_es if lang == "es" else caption_en
        figures.append(
            f'<figure><img src="{esc(quote(src, safe="/"))}" width="{width}" height="{height}" alt="{esc(caption)}" loading="lazy" decoding="async" />'
            f'<figcaption>{esc(caption)}</figcaption></figure>'
        )
    if not figures:
        return ""
    heading = "Evidencia visual" if lang == "es" else "Visual evidence"
    eyebrow = "EVIDENCIA" if lang == "es" else "EVIDENCE"
    return f'<section class="case-section"><div class="home-shell"><div class="case-heading"><p class="eyebrow">{eyebrow}</p><h2>{heading}</h2></div><div class="visual-grid">{"".join(figures)}</div></div></section>'


def render_technical(data: dict[str, object], lang: str) -> str:
    if not data.get("technical"):
        return ""
    heading = "Profundidad técnica" if lang == "es" else "Technical depth"
    intro = (
        "Las decisiones se conectaron en cuatro capas operativas; estos son los criterios aplicados."
        if lang == "es"
        else "Decisions were connected across four operating layers; these are the criteria applied."
    )
    cards = "".join(
        f'<article class="technical-card"><h3>{esc(title)}</h3><p>{esc(copy)}</p></article>'
        for title, copy in data["technical"]
    )
    eyebrow = "NOTA TÉCNICA" if lang == "es" else "TECHNICAL NOTE"
    return f'<section class="case-section"><div class="home-shell"><div class="case-heading"><p class="eyebrow">{eyebrow}</p><h2>{heading}</h2><p class="case-deck">{intro}</p></div><div class="technical-grid">{cards}</div></div></section>'


def render_case(case_id: str, case: dict[str, object], claims: dict[str, object], lang: str, default: bool = False) -> str:
    data = case[lang]
    claim = claims[case_id]
    slug = case["slug"]
    suffix = "" if default else f"-{lang}"
    canonical = f"https://matiasgaglio.onrender.com/{slug}{suffix}.html"
    spanish = lang == "es"
    labels = {
        "skip_label": "Saltar al contenido principal" if spanish else "Skip to main content",
        "home_label": "Inicio" if spanish else "Home",
        "nav_label": "Navegación principal" if spanish else "Primary navigation",
        "contact_short": "Hablemos" if spanish else "Contact me",
        "switch_aria": "View in English" if spanish else "Ver en español",
        "menu_open": "Abrir menú" if spanish else "Open menu",
        "menu_close": "Cerrar menú" if spanish else "Close menu",
        "context_title": "Cliente y contexto" if spanish else "Client and context",
        "problem_title": "Problema y diagnóstico" if spanish else "Problem and diagnosis",
        "diagnosis_title": "Diagnóstico" if spanish else "Diagnosis",
        "role_title": "Mi rol" if spanish else "My role",
        "actions_title": "Decisiones e intervenciones" if spanish else "Decisions and interventions",
        "results_title": "Resultados" if spanish else "Results",
        "learning_title": "Qué aprendí" if spanish else "What I learned",
        "disclosure_label": "Nota de evidencia" if spanish else "Evidence note",
        "source_label": "Fuente:" if spanish else "Source:",
        "cta_eyebrow": "Próximo paso" if spanish else "Next step",
        "cta_button": "Hablemos sobre tu proyecto" if spanish else "Discuss your project",
        "back_label": "Ver más casos" if spanish else "View more cases",
    }
    facts_labels = (
        [("Período", claim["period_analyzed"][lang]), ("Línea base", claim["baseline"][lang]), ("Resultado final", claim["final_result"][lang])]
        if spanish
        else [("Period", claim["period_analyzed"][lang]), ("Baseline", claim["baseline"][lang]), ("Final outcome", claim["final_result"][lang])]
    )
    facts = "".join(f'<div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>' for label, value in facts_labels)
    values = {
        "global_nav": render_global_nav(lang, f"{slug}-en.html" if spanish else f"{slug}-es.html"),
        **labels,
        "lang": lang,
        "locale": "es_AR" if spanish else "en_US",
        "title": esc(data.get("seo_title", f'{data["title"]} | Matías Gaglio')),
        "description": esc(data["description"]),
        "canonical": canonical,
        "alternate_es": f"https://matiasgaglio.onrender.com/{slug}-es.html",
        "alternate_en": f"https://matiasgaglio.onrender.com/{slug}-en.html",
        "home_href": "index.html" if spanish else "index-en.html",
        "nav_items": render_nav(lang),
        "switch_href": f"{slug}-en.html" if spanish else f"{slug}-es.html",
        "switch_lang": "en" if spanish else "es",
        "switch_label": "EN" if spanish else "ES",
        "category": esc(data["category"]),
        "heading": esc(data["title"]),
        "deck": esc(data["deck"]),
        "facts": facts,
        "context": esc(data["context"]),
        "disclosure": esc(claim["disclosure"][lang]),
        "problem": esc(data["problem"]),
        "diagnosis": esc(data["diagnosis"]),
        "role": esc(data["role"]),
        "actions": render_actions(data["actions"]),
        "technical_block": render_technical(data, lang),
        "visual_block": render_visuals(case, lang),
        "results": render_results(claim, lang),
        "implication": esc(data["implication"]),
        "source": esc(claim["measurement_source"]),
        "learning": esc(data["learning"]),
        "cta_title": esc(data["cta_title"]),
        "cta_copy": esc(data["cta_copy"]),
        "back_href": "ecommerce-es.html#cases" if spanish else "ecommerce-en.html#cases",
    }
    return Template(TEMPLATE.read_text(encoding="utf-8")).substitute(values).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    cases = json.loads(CONTENT.read_text(encoding="utf-8"))
    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))
    expected: dict[Path, str] = {}
    for case_id, case in cases.items():
        slug = case["slug"]
        expected[ROOT / f"{slug}-es.html"] = render_case(case_id, case, claims, "es")
        expected[ROOT / f"{slug}-en.html"] = render_case(case_id, case, claims, "en")
        expected[ROOT / f"{slug}.html"] = render_case(case_id, case, claims, "es", default=True)
    stale = []
    for path, content in expected.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path.name)
        else:
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"Built {path.name}")
    if stale:
        print("Stale generated case studies: " + ", ".join(stale))
        return 1
    if args.check:
        print("Generated case studies are current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
