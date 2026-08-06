"""Build bilingual interactive HTML resume pages from the verified PDF resume content."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from string import Template

from resume_content import COPY
from shared_nav import render_global_nav

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "cv.html"
CLAIMS = json.loads((ROOT / "content" / "project-claims.json").read_text(encoding="utf-8"))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


CASE_META = [
    ("case_1", "caso-1-es.html", "caso-1-en.html"),
    ("case_2", "caso-2-es.html", "caso-2-en.html"),
    ("daizzy", "caso-daizzy-gear-es.html", "caso-daizzy-gear-en.html"),
]


UI = {
    "es": {
        "title": "CV interactivo de Matías Gaglio | Ecommerce, Amazon Growth y BI",
        "description": "CV interactivo de Matías Gaglio: perfil, evidencia, herramientas y formación en Ecommerce, Amazon Growth, PPC y Business Intelligence.",
        "hero_eyebrow": "CV interactivo · Perfil profesional",
        "download_label": "Descargar PDF",
        "contact_label": "Contactarme",
        "print_label": "Imprimir",
        "current_label": "Rol actual",
        "focus_label": "Foco profesional",
        "location_label": "Ubicación",
        "remote_label": "Remoto",
        "cv_nav_label": "Secciones del CV",
        "profile_label": "Perfil",
        "evidence_label": "Evidencia",
        "approach_label": "Método",
        "skills_label": "Herramientas",
        "education_label": "Formación",
        "sidebar_note": "Lectura breve para reclutadores y colaboradores. El PDF descargable conserva la versión imprimible.",
        "sidebar_label": "Índice del CV",
        "profile_kicker": "Resumen",
        "profile_title": "Datos, pauta y contenido como un solo sistema.",
        "profile_copy": "Trabajo en la intersección entre comportamiento del cliente, rendimiento comercial y ejecución creativa. Mi aporte es convertir señales dispersas en una decisión priorizada, implementable y medible.",
        "focus_cards": [
            ("Ecommerce & Amazon", "Operación y crecimiento", "Listings, PPC, SEO, CRO, inventario y catálogo conectados por etapa del producto."),
            ("Business Intelligence", "Rentabilidad y diagnóstico", "Ventas, inversión, conversión y margen traducidos en prioridades de portafolio."),
            ("Data-to-Creative", "Evidencia que comunica", "VOC, especificaciones y rendimiento convertidos en contenido que ayuda a decidir."),
        ],
        "evidence_kicker": "Casos seleccionados",
        "evidence_title": "Resultados con contexto y límites claros.",
        "evidence_intro": "Cada caso separa el resultado observado, mi intervención y aquello que los datos disponibles todavía no permiten afirmar.",
        "expand_label": "Abrir todos",
        "collapse_label": "Cerrar todos",
        "contribution_label": "Mi intervención",
        "caveat_label": "Límite de lectura",
        "case_link": "Ver caso completo",
        "approach_kicker": "Forma de trabajo",
        "approach_title": "Del diagnóstico a una decisión verificable.",
        "skills_kicker": "Stack profesional",
        "skills_title": "Herramientas al servicio del criterio.",
        "skill_groups": [
            ("Amazon & Ecommerce", ["Seller Central", "Amazon Ads", "SEO", "CRO", "Arquitectura de listings"]),
            ("Datos & BI", ["SQL", "Python", "R", "Power BI", "GA4", "Google Ads", "Reporting comercial"]),
            ("Creatividad & Sistemas", ["Diseño visual", "3D", "Automatización", "Data-to-Creative"]),
        ],
        "education_kicker": "Formación",
        "education_title": "Comunicación para entender; datos para decidir.",
        "education_institution": ["Universidad de Buenos Aires (UBA)", "Universidad Favaloro"],
        "availability_label": "Disponibilidad",
        "home_label": "Inicio",
        "skip_label": "Saltar al contenido principal",
    },
    "en": {
        "title": "Matías Gaglio Interactive Resume | Ecommerce, Amazon Growth & BI",
        "description": "Matías Gaglio's interactive resume: profile, evidence, tools and education across Ecommerce, Amazon Growth, PPC and Business Intelligence.",
        "hero_eyebrow": "Interactive resume · Professional profile",
        "download_label": "Download PDF",
        "contact_label": "Contact me",
        "print_label": "Print",
        "current_label": "Current role",
        "focus_label": "Professional focus",
        "location_label": "Location",
        "remote_label": "Remote",
        "cv_nav_label": "Resume sections",
        "profile_label": "Profile",
        "evidence_label": "Evidence",
        "approach_label": "Method",
        "skills_label": "Tools",
        "education_label": "Education",
        "sidebar_note": "A concise view for recruiters and collaborators. The downloadable PDF preserves the print-ready version.",
        "sidebar_label": "Resume index",
        "profile_kicker": "Summary",
        "profile_title": "Data, media and content as one system.",
        "profile_copy": "I work at the intersection of customer behavior, commercial performance and creative execution. My contribution is turning scattered signals into a prioritized, executable and measurable decision.",
        "focus_cards": [
            ("Ecommerce & Amazon", "Operations and growth", "Listings, PPC, SEO, CRO, inventory and catalog connected by product stage."),
            ("Business Intelligence", "Profitability and diagnosis", "Sales, spend, conversion and margin translated into portfolio priorities."),
            ("Data-to-Creative", "Evidence that communicates", "VOC, specifications and performance turned into content that supports decisions."),
        ],
        "evidence_kicker": "Selected cases",
        "evidence_title": "Outcomes with context and clear limits.",
        "evidence_intro": "Each case separates the observed result, my intervention and what the available evidence cannot yet support.",
        "expand_label": "Open all",
        "collapse_label": "Close all",
        "contribution_label": "My intervention",
        "caveat_label": "Reading limit",
        "case_link": "View full case",
        "approach_kicker": "Working approach",
        "approach_title": "From diagnosis to a verifiable decision.",
        "skills_kicker": "Professional stack",
        "skills_title": "Tools in service of judgment.",
        "skill_groups": [
            ("Amazon & Ecommerce", ["Seller Central", "Amazon Ads", "SEO", "CRO", "Listing architecture"]),
            ("Data & BI", ["SQL", "Python", "R", "Power BI", "GA4", "Google Ads", "Commercial reporting"]),
            ("Creative & Systems", ["Visual design", "3D", "Automation", "Data-to-Creative"]),
        ],
        "education_kicker": "Education",
        "education_title": "Communication to understand; data to decide.",
        "education_institution": ["University of Buenos Aires (UBA)", "Favaloro University"],
        "availability_label": "Availability",
        "home_label": "Home",
        "skip_label": "Skip to main content",
    },
}


def render(lang: str, default: bool = False) -> str:
    es = lang == "es"
    content = COPY[lang]
    ui = UI[lang]
    slug = "cv" if default else f"cv-{lang}"
    focus_cards = "".join(
        f'<article><span>0{index}</span><h3>{esc(title)}</h3><p>{esc(copy)}</p></article>'
        for index, (_, title, copy) in enumerate(ui["focus_cards"], 1)
    )
    cases = []
    for index, ((title, metric, contribution), (claim_key, href_es, href_en)) in enumerate(zip(content["cases"], CASE_META), 1):
        claim = CLAIMS[claim_key]
        caveat = claim["disclosure"][lang]
        href = href_es if es else href_en
        cases.append(
            f'<details class="cv-case"{ " open" if index == 1 else "" }>'
            f'<summary><span class="cv-case__index">0{index}</span><h3>{esc(title)}</h3><span class="cv-case__metric">{esc(metric)}</span><span class="cv-case__toggle" aria-hidden="true">+</span></summary>'
            f'<div class="cv-case__body"><div><p><strong>{esc(ui["contribution_label"])}:</strong> {esc(contribution)}</p><a href="{href}">{esc(ui["case_link"])} ↗</a></div>'
            f'<div class="cv-case__note"><small><strong>{esc(ui["caveat_label"])}:</strong> {esc(caveat)}</small></div></div></details>'
        )
    approach_steps = "".join(f"<li><strong>{esc(step.strip())}</strong></li>" for step in content["approach_value"].split(" - "))
    skill_groups = "".join(
        f'<article class="cv-skill-group"><h3>{esc(title)}</h3><ul>{"".join(f"<li>{esc(tool)}</li>" for tool in tools)}</ul></article>'
        for title, tools in ui["skill_groups"]
    )
    education_values = content["education_value"].split("\n")
    education_items = "".join(
        f'<article><span>0{index}</span><h3>{esc(value.split(",", 1)[0])}</h3><p>{esc(ui["education_institution"][index - 1])}</p></article>'
        for index, value in enumerate(education_values, 1)
    )
    structured = {
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "url": f"https://matiasgaglio.onrender.com/{slug}.html",
        "inLanguage": lang,
        "mainEntity": {
            "@type": "Person",
            "name": "Matías Gaglio",
            "jobTitle": content["role"],
            "email": "mailto:matiasignaciogaglio@gmail.com",
            "sameAs": ["https://linkedin.com/in/matiasignaciogaglio", "https://github.com/MynosIII"],
        },
    }
    values = {
        **{key: esc(value) for key, value in ui.items() if isinstance(value, str)},
        "lang": lang,
        "canonical": f"https://matiasgaglio.onrender.com/{slug}.html",
        "global_nav": render_global_nav(lang, "cv-en.html" if es else "cv-es.html"),
        "structured_data": json.dumps(structured, ensure_ascii=False).replace("</", "<\\/"),
        "role": esc(content["role"]),
        "summary": esc(content["summary"]),
        "pdf_href": f'output/pdf/{content["file"]}',
        "current_value": esc(content["current_value"]),
        "focus_value": esc(content["expertise_value"]),
        "remote_label": esc(ui["remote_label"]),
        "focus_cards": focus_cards,
        "case_cards": "".join(cases),
        "approach_steps": approach_steps,
        "skill_groups": skill_groups,
        "education_items": education_items,
        "availability_value": esc(content["availability_value"]),
        "home_href": "index-es.html" if es else "index-en.html",
    }
    return Template(TEMPLATE.read_text(encoding="utf-8")).substitute(values).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = {
        ROOT / "cv-es.html": render("es"),
        ROOT / "cv-en.html": render("en"),
        ROOT / "cv.html": render("es", default=True),
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
        print("Stale generated CV pages: " + ", ".join(stale))
        return 1
    if args.check:
        print("Generated CV pages are current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
