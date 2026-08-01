# Matías Gaglio portfolio

This repository is the source of truth for the static site deployed at <https://matiasgaglio.onrender.com>. Render deploys the `main` branch of `MynosIII/WebPage`; edits made to ZIP extractions or unrelated local folders do not deploy.

## Maintenance

- Edit the explicit English (`*-en.html`) and Spanish (`*-es.html`) pages together.
- Treat un-suffixed localized pages as legacy aliases. Their canonical metadata points to the matching explicit-language page.
- Run `python scripts/normalize_site.py` after adding or renaming pages. It keeps canonical, hreflang, social metadata, favicon references, the pinned AOS version, and shared footer years consistent.
- Run `python scripts/validate_site.py` before publishing. It checks internal files and anchors, filename casing, metadata, image alt text, and files that should never be deployed.
- Regenerate the social card with `python scripts/generate_social_card.py` if its copy or visual design changes.

Source documents, spreadsheets, and captured third-party webpages do not belong in this public deployment repository. Keep them in the private source archive instead.
