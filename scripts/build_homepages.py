"""Build the localized homepages from one content source and one template."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from string import Template


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "homepage.json"
CLAIMS = ROOT / "content" / "project-claims.json"
TEMPLATE = ROOT / "templates" / "homepage.html"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def nav_items(items: list[list[str]]) -> str:
    return "".join(f'<li><a href="{esc(href)}">{esc(label)}</a></li>' for label, href in items)


def proof_items(items: list[list[str]]) -> str:
    return "".join(
        f'<div><strong>{esc(value)}</strong><span>{esc(label)}</span></div>' for value, label in items
    )


def capability_items(items: list[list[str]]) -> str:
    return "".join(
        '<article class="capability-card">'
        f'<span>{esc(index)}</span><h3>{esc(title)}</h3><p>{esc(copy)}</p>'
        "</article>"
        for index, title, copy in items
    )


def picture(item: dict[str, object]) -> str:
    if item.get("image_src"):
        return (
            f'<img src="{esc(item["image_src"])}" width="{int(item["image_width"])}" '
            f'height="{int(item["image_height"])}" alt="{esc(item["image_alt"])}" '
            'loading="lazy" decoding="async" />'
        )
    slug = str(item["image"])
    width = int(item["image_width"])
    height = int(item["image_height"])
    widths = sorted({min(640, width), min(1200, width)})
    sources = ", ".join(f"assets/home/{slug}-{candidate}.webp {candidate}w" for candidate in widths)
    fallback = widths[0]
    return (
        f'<img src="assets/home/{slug}-{fallback}.webp" srcset="{sources}" '
        f'sizes="(max-width: 760px) 100vw, 48vw" width="{width}" height="{height}" '
        f'alt="{esc(item["image_alt"])}" loading="lazy" decoding="async" />'
    )


def research_visual(label: str) -> str:
    return (
        '<div class="research-visual" aria-hidden="true">'
        '<span class="research-visual__label">' + esc(label) + "</span>"
        '<div class="research-visual__plot"><i style="--h:34%"></i><i style="--h:62%"></i>'
        '<i style="--h:46%"></i><i style="--h:81%"></i><i style="--h:68%"></i>'
        '<i style="--h:92%"></i><i style="--h:72%"></i></div>'
        '<div class="research-visual__axis"><span>OBSERVE</span><span>MODEL</span><span>EXPLAIN</span></div>'
        "</div>"
    )


def work_items(items: list[dict[str, object]], claims: dict[str, object], lang: str) -> str:
    output: list[str] = []
    problem_label = "Problema" if lang == "es" else "Problem"
    intervention_label = "Intervención" if lang == "es" else "Intervention"
    for item in items:
        visual = (
            picture(item)
            if item.get("image") or item.get("image_src")
            else research_visual(str(item["visual_label"]))
        )
        claim = claims[str(item["claim_id"])]
        metrics = "".join(
            f"<li>{esc(metric)}</li>" for metric in claim["approved_public_claims"][lang]
        )
        output.append(
            '<article class="work-card">'
            f'<a class="work-card__media" href="{esc(item["href"])}" tabindex="-1" aria-hidden="true">{visual}</a>'
            '<div class="work-card__body">'
            f'<div class="work-card__meta"><span>{esc(item["index"])}</span><p>{esc(item["category"])}</p></div>'
            f'<h3>{esc(item["title"])}</h3>'
            f'<p class="work-card__summary"><strong>{problem_label}:</strong> {esc(item["problem"])}</p>'
            f'<p class="work-card__summary"><strong>{intervention_label}:</strong> {esc(item["intervention"])}</p>'
            f'<ul class="work-card__metrics">{metrics}</ul>'
            f'<a class="text-link" href="{esc(item["href"])}">{esc(item["cta"])} <span aria-hidden="true">↗</span></a>'
            "</div></article>"
        )
    return "".join(output)


def method_items(items: list[list[str]]) -> str:
    return "".join(
        f'<li><span>{esc(index)}</span><h3>{esc(title)}</h3><p>{esc(copy)}</p></li>'
        for index, title, copy in items
    )


def library_items(items: list[list[str]]) -> str:
    return "".join(
        f'<a class="library-card" href="{esc(href)}"><span class="library-card__index">{index:02d}</span>'
        f'<h3>{esc(title)}</h3><p>{esc(copy)}</p><span class="library-card__arrow" aria-hidden="true">↗</span></a>'
        for index, (title, copy, href) in enumerate(items, start=1)
    )


def structured_data(locale: dict[str, object]) -> str:
    spanish = locale["lang"] == "es"
    payload = {
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "@id": f'{locale["canonical"]}#profile-page',
        "url": locale["canonical"],
        "name": locale["title"],
        "description": locale["description"],
        "inLanguage": locale["lang"],
        "mainEntity": {
            "@type": "Person",
            "@id": "https://matiasgaglio.onrender.com/#matias-gaglio",
            "name": "Matías Gaglio",
            "url": "https://matiasgaglio.onrender.com/",
            "email": "mailto:matiasignaciogaglio@gmail.com",
            "sameAs": [
                "https://linkedin.com/in/matiasignaciogaglio",
                "https://github.com/MynosIII",
            ],
            "jobTitle": "Ecommerce & Amazon Growth Strategist",
            "knowsAbout": [
                "Ecommerce strategy",
                "Business Intelligence",
                "Amazon PPC",
                "Search engine optimization",
                "Conversion rate optimization",
                "Creative direction",
                "Voice of Customer research",
            ],
            "description": (
                "Estratega de ecommerce y Business Intelligence que conecta datos, rendimiento y sistemas creativos."
                if spanish
                else "Ecommerce and Business Intelligence strategist connecting data, performance and creative systems."
            ),
        },
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def render(locale: dict[str, object], claims: dict[str, object]) -> str:
    spanish = locale["lang"] == "es"
    values = {key: esc(value) for key, value in locale.items() if not isinstance(value, (list, dict))}
    values.update(
        {
            "structured_data": structured_data(locale),
            "skip_label": "Saltar al contenido principal" if spanish else "Skip to main content",
            "back_to_top": "Volver arriba" if spanish else "Back to top",
            "home_href": "index.html" if spanish else "index-en.html",
            "home_id": "inicio" if spanish else "home",
            "switch_hreflang": "en" if spanish else "es",
            "primary_href": "#trabajo" if spanish else "#work",
            "secondary_href": "#contacto" if spanish else "#contact",
            "cv_href": "output/pdf/Matias-Gaglio-CV-ES.pdf" if spanish else "output/pdf/Matias-Gaglio-Resume-EN.pdf",
            "signal_data": "DATOS" if spanish else "DATA",
            "signal_data_copy": "Encontrar la señal" if spanish else "Find the signal",
            "signal_strategy": "ESTRATEGIA" if spanish else "STRATEGY",
            "signal_strategy_copy": "Elegir la acción" if spanish else "Choose the move",
            "signal_creative": "CONTENIDO" if spanish else "CREATIVE",
            "signal_creative_copy": "Comunicar con claridad" if spanish else "Make it clear",
            "signal_measure": "MEDIR" if spanish else "MEASURE",
            "capabilities_id": "capacidades" if spanish else "capabilities",
            "library_id": "trabajo" if spanish else "work",
            "work_id": "casos" if spanish else "cases",
            "method_id": "metodo" if spanish else "method",
            "contact_id": "contacto" if spanish else "contact",
            "about_href": "sobre-mi-es.html" if spanish else "sobre-mi-en.html",
            "nav_items": nav_items(locale["nav"]),
            "proof_items": proof_items(locale["proof"]),
            "capability_items": capability_items(locale["capabilities"]),
            "work_items": work_items(locale["work"], claims, str(locale["lang"])),
            "method_items": method_items(locale["method"]),
            "library_items": library_items(locale["library"]),
        }
    )
    return Template(TEMPLATE.read_text(encoding="utf-8")).substitute(values).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if committed output is stale")
    args = parser.parse_args()
    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))
    expected = {
        ROOT / "index.html": render(data["es"], claims),
        ROOT / "index-es.html": render(data["es"], claims),
        ROOT / "index-en.html": render(data["en"], claims),
    }
    stale: list[str] = []
    for path, content in expected.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path.name)
        else:
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"Built {path.relative_to(ROOT)}")
    if stale:
        print("Stale generated homepage files: " + ", ".join(stale))
        return 1
    if args.check:
        print("Generated homepage files are current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
