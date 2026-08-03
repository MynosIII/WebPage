"""Keep the main Ecommerce case cards aligned with verified project claims."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
CLAIMS = json.loads((ROOT / "content" / "project-claims.json").read_text(encoding="utf-8"))


CARD_COPY = {
    "es": {
        "case_1": ("Amazon Growth & PPC", "Pauta, listing y conversión como un solo sistema", "Auditoría y reestructuración de campañas, segmentación y contenido. Las comparaciones usan ventanas explícitas y se presentan como evidencia observacional.", ["Caso1_plot.jpeg", "Caso1_conversions.png"]),
        "case_2": ("Business Intelligence y rentabilidad", "De reportar ventas a decidir con margen", "Lectura mensual de ventas, publicidad y beneficio neto estimado para priorizar el portafolio por causa, oportunidad y riesgo.", ["Caso2.jpeg"]),
        "case_3": ("Data-to-Creative · Amazon Gallery", "Información técnica convertida en una galería de decisión", "Rediseño de seis imágenes para hacer visibles especificaciones, compatibilidad y beneficios. No se publica un cambio de conversión porque no existe una prueba controlada en el archivo.", ["Revolution/Old Style Images/61dHW0lmqEL._AC_SL1500_.jpg", "Revolution/New Style Images/61HEg-LnYyL._AC_SL1400_.jpg"]),
        "daizzy": ("Amazon Account Management · Caso técnico", "Daizzy Gear: PPC, inventario y contenido coordinados", "Caso técnico sobre arquitectura PPC, presupuesto, inventario, promociones, A+ Content, Brand Store y catálogo, con una recuperación semanal contextualizada.", ["image_060.png", "image_079.png"]),
    },
    "en": {
        "case_1": ("Amazon Growth & PPC", "Media, listings and conversion as one system", "Campaign, targeting and content audit and restructuring. Comparisons use explicit windows and are presented as observational evidence.", ["Caso1_plot.jpeg", "Caso1_conversions.png"]),
        "case_2": ("Business Intelligence and profitability", "From sales reporting to margin-led decisions", "A monthly sales, media and estimated net-profit view used to prioritize the portfolio by cause, opportunity and risk.", ["Caso2.jpeg"]),
        "case_3": ("Data-to-Creative · Amazon Gallery", "Technical information turned into a decision gallery", "Six images redesigned to make specifications, compatibility and benefits visible. No conversion change is published because the archive contains no controlled test.", ["Revolution/Old Style Images/61dHW0lmqEL._AC_SL1500_.jpg", "Revolution/New Style Images/61HEg-LnYyL._AC_SL1400_.jpg"]),
        "daizzy": ("Amazon Account Management · Technical case", "Daizzy Gear: coordinated PPC, inventory and content", "A technical case covering PPC architecture, budget, inventory, promotions, A+ Content, Storefront and catalog, with a contextualized weekly recovery.", ["image_060.png", "image_079.png"]),
    },
}


SIZES = {
    "Caso1_plot.jpeg": (794, 352),
    "Caso1_conversions.png": (850, 388),
    "Caso2.jpeg": (1024, 268),
    "Revolution/Old Style Images/61dHW0lmqEL._AC_SL1500_.jpg": (1500, 892),
    "Revolution/New Style Images/61HEg-LnYyL._AC_SL1400_.jpg": (1368, 1312),
    "image_060.png": (1178, 811),
    "image_079.png": (1277, 612),
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def card(case_id: str, lang: str, delay: int, default: bool = False) -> str:
    category, title, copy, images = CARD_COPY[lang][case_id]
    claim = CLAIMS[case_id]
    slug = {"case_1": "caso-1", "case_2": "caso-2", "case_3": "caso-3", "daizzy": "caso-daizzy-gear"}[case_id]
    reverse = " reverse" if case_id in {"case_2", "daizzy"} else ""
    metrics = "".join(f'<li><span class="accent">{esc(metric)}</span></li>' for metric in claim["approved_public_claims"][lang])
    image_html = "".join(
        f'<img src="{esc(quote(src, safe="/"))}" alt="{esc(title)}" loading="lazy" width="{SIZES[src][0]}" height="{SIZES[src][1]}" decoding="async">'
        for src in images
    )
    href = f"{slug}.html" if default else f"{slug}-{lang}.html"
    return f'''        <a href="{href}" class="caso-card-link" data-aos="fade-up" data-aos-delay="{delay}">
          <article class="caso-card{reverse}">
            <span class="caso-categoria">{esc(category)}</span>
            <h3>{esc(title)}</h3>
            <div class="caso-card-grid">
              <div class="caso-contenido">
                <p>{esc(copy)}</p>
                <ul class="caso-metricas">{metrics}</ul>
              </div>
              <div class="caso-visual">{image_html}</div>
            </div>
          </article>
        </a>'''


def sync(content: str, lang: str, default: bool = False) -> str:
    delays = {"case_1": 200, "case_2": 300, "case_3": 400, "daizzy": 500}
    slugs = {"case_1": "caso-1", "case_2": "caso-2", "case_3": "caso-3", "daizzy": "caso-daizzy-gear"}
    for case_id, slug in slugs.items():
        href = rf'{re.escape(slug)}\.html' if default else rf'{re.escape(slug)}-{lang}\.html'
        pattern = rf'\s*<a href="{href}" class="caso-card-link"[^>]*>.*?</a>'
        replacement = "\n" + card(case_id, lang, delays[case_id], default)
        content, count = re.subn(pattern, replacement, content, count=1, flags=re.DOTALL)
        if count != 1:
            raise RuntimeError(f"Could not locate {slug}-{lang}.html card")
    return content.rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    targets = [("es", ROOT / "ecommerce-es.html", False), ("en", ROOT / "ecommerce-en.html", False), ("es", ROOT / "ecommerce.html", True)]
    for lang, path, default in targets:
        current = path.read_text(encoding="utf-8")
        expected = sync(current, lang, default)
        if args.check:
            if current != expected:
                stale.append(path.name)
        else:
            path.write_text(expected, encoding="utf-8", newline="\n")
            print(f"Updated {path.name}")
    if stale:
        print("Stale Ecommerce claims: " + ", ".join(stale))
        return 1
    if args.check:
        print("Ecommerce claims are current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
