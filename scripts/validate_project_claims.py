"""Validate credibility guardrails for the public project claims."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS_PATH = ROOT / "content" / "project-claims.json"
HOMEPAGE_PATH = ROOT / "content" / "homepage.json"
REQUIRED = {"project_name", "period_analyzed", "baseline", "final_result", "percentage_change", "contribution", "measurement_source", "approved_public_claims", "disclosure"}


def main() -> int:
    errors: list[str] = []
    claims = json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))
    homepage = json.loads(HOMEPAGE_PATH.read_text(encoding="utf-8"))
    for case_id, claim in claims.items():
        missing = REQUIRED - set(claim)
        if missing:
            errors.append(f"{case_id}: missing fields {sorted(missing)}")
        for field in REQUIRED - {"measurement_source"}:
            if field in claim and isinstance(claim[field], dict):
                for lang in ("es", "en"):
                    if not claim[field].get(lang):
                        errors.append(f"{case_id}.{field}.{lang}: empty")
    for lang in ("es", "en"):
        work = homepage[lang]["work"]
        if len(work) != 3:
            errors.append(f"homepage.{lang}.work must contain exactly three flagship cases")
        ids = [item.get("claim_id") for item in work]
        if ids != ["case_1", "case_2", "case_3"]:
            errors.append(f"homepage.{lang}.work must use case_1, case_2 and case_3 in order")
    public_pages = [
        ROOT / name
        for name in (
            "index.html", "index-es.html", "index-en.html", "ecommerce.html", "ecommerce-es.html", "ecommerce-en.html",
            "caso-1.html", "caso-1-es.html", "caso-1-en.html", "caso-2.html", "caso-2-es.html", "caso-2-en.html",
            "caso-3.html", "caso-3-es.html", "caso-3-en.html", "caso-daizzy-gear.html", "caso-daizzy-gear-es.html", "caso-daizzy-gear-en.html",
        )
    ]
    forbidden = ["+100%", "+150%", "+50% ROAS", "-30%", "+12%", "USD 2.504", "USD 2,504", "conversión global cerca de un 120%", "overall conversion by around 120%"]
    for path in public_pages:
        text = html.unescape(path.read_text(encoding="utf-8"))
        for phrase in forbidden:
            if phrase.casefold() in text.casefold():
                errors.append(f"{path.name}: unsupported or retired claim '{phrase}'")
    for pdf in (ROOT / "output" / "pdf" / "Matias-Gaglio-CV-ES.pdf", ROOT / "output" / "pdf" / "Matias-Gaglio-Resume-EN.pdf"):
        if not pdf.exists() or pdf.stat().st_size < 10_000:
            errors.append(f"Missing or invalid resume PDF: {pdf.relative_to(ROOT)}")
    if errors:
        print("Project-claim validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Project claims, flagship selection and resume links are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
