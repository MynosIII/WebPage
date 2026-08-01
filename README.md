# Matías Gaglio portfolio

This repository is the source of truth for the bilingual static portfolio deployed at <https://matiasgaglio.onrender.com>. Render deploys the `main` branch of `MynosIII/WebPage`; ZIP extractions and unrelated local folders do not deploy.

## Site architecture

- `/` serves the Spanish homepage directly. `/index-en.html` is its English counterpart and `/index-es.html` remains a backwards-compatible Spanish URL.
- `content/homepage.json` is the bilingual content source for all three homepage files; the homepage combines three evidence-led flagship cases with a prominent directory of the complete portfolio.
- `content/project-claims.json` is the credibility source of truth for every public metric, period, baseline, contribution, source, approved claim, and evidence note in the flagship and Daizzy cases.
- `content/case-studies.json` and `templates/case-study.html` generate the standardized Case 1, Case 2, Case 3, and Daizzy pages.
- `content/about.json` and `templates/about.html` generate the recruiter-focused professional story.
- `templates/homepage.html`, `home.css`, and `home.js` contain the shared homepage structure, visual system, and interaction behavior.
- `scripts/build_homepages.py` generates the committed homepage HTML. Generated files should never be edited directly.
- Downloadable Spanish and English resumes are generated into `output/pdf/` by `scripts/build_resumes.py` and are linked from the main navigation, hero, and About page.
- Additional case-study pages remain static HTML and use `style.css` plus `accessibility.js` while they are progressively migrated to shared templates.
- `language-catalog.json` defines the 39 Spanish/English page pairs. `scripts/apply_legacy_translation_fixes.py` preserves the reviewed legacy glossary, while `scripts/validate_localization.py` checks language declarations, reciprocal `hreflang`, encoding, and banned literal translations.
- `robots.txt` and `sitemap.xml` are generated from canonical page metadata.

## Local preview

Python is sufficient for the website itself:

```bash
python -m http.server 8000
```

Open <http://localhost:8000>. For image generation, install Pillow. Browser regression tests additionally require Node.js 22 and Chromium:

```bash
python -m pip install Pillow==11.3.0
npm install
npx playwright install chromium
npm test
```

## Editing and validation

After changing homepage content or its template:

```bash
python scripts/generate_home_assets.py
python scripts/build_homepages.py
python scripts/build_case_studies.py
python scripts/build_about_pages.py
python scripts/sync_ecommerce_claims.py
python scripts/apply_legacy_translation_fixes.py
python scripts/generate_sitemap.py
python scripts/validate_site.py
```

Before publishing, also run:

```bash
python scripts/build_homepages.py --check
python scripts/build_case_studies.py --check
python scripts/build_about_pages.py --check
python scripts/sync_ecommerce_claims.py --check
python scripts/apply_legacy_translation_fixes.py --check
python scripts/validate_localization.py
python scripts/validate_project_claims.py
python scripts/generate_sitemap.py --check
python scripts/add_image_dimensions.py --check
npm run validate:html
npm test
npm run lighthouse
```

To regenerate the resumes, install ReportLab and run `python scripts/build_resumes.py`. Render both PDFs to PNG before committing and inspect them for clipping or overflow. `scripts/normalize_site.py` maintains canonical, hreflang, social, favicon, AOS, and footer conventions on legacy pages. It intentionally excludes generated pages. `scripts/add_image_dimensions.py` adds intrinsic dimensions to local raster images without reformatting the surrounding HTML.

GitHub Actions repeats link/casing/metadata validation, responsive checks at 390, 820, 1024, and 1440 px, automated accessibility checks, screenshots, and Lighthouse budgets on every pull request.

## Render deployment

The reproducible service definition is in `render.yaml`:

- service type: Static Site
- repository: `MynosIII/WebPage`
- branch: `main`
- build command: generated homepage, case-study, About, Ecommerce claim, discovery, credibility, and site-validation checks from `render.yaml`
- publish directory: `.`
- auto-deploy: enabled for `main`
- pull-request previews: disabled

The Blueprint also documents the security and cache headers. Render serves the static output through its CDN, forces HTTPS, and atomically invalidates its CDN cache after a successful deploy.

## Asset policy

Commit optimized page images with explicit dimensions and use responsive WebP sources for homepage media. Source documents, spreadsheets, downloaded third-party webpages, and editable production assets belong in the private source archive—not this public deploy repository.

The existing large showcase videos are intentionally unchanged for now because migrating already-published video payloads requires a confirmed object-storage/CDN destination or a coordinated Git LFS rollout. New large binary media should not be added directly to Git history.
