# Matías Gaglio portfolio

This repository is the source of truth for the bilingual static portfolio deployed at <https://matiasgaglio.onrender.com>. Render deploys the `main` branch of `MynosIII/WebPage`; ZIP extractions and unrelated local folders do not deploy.

## Site architecture

- `/` serves the Spanish homepage directly. `/index-en.html` is its English counterpart and `/index-es.html` remains a backwards-compatible Spanish URL.
- `content/homepage.json` is the single bilingual content source for all three homepage files.
- `templates/homepage.html`, `home.css`, and `home.js` contain the shared homepage structure, visual system, and interaction behavior.
- `scripts/build_homepages.py` generates the committed homepage HTML. Generated files should never be edited directly.
- Older case-study pages remain static HTML and use `style.css` plus `accessibility.js` while they are progressively migrated to shared templates.
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
python scripts/generate_sitemap.py
python scripts/validate_site.py
```

Before publishing, also run:

```bash
python scripts/build_homepages.py --check
python scripts/generate_sitemap.py --check
python scripts/add_image_dimensions.py --check
npm run validate:html
npm test
npm run lighthouse
```

`scripts/normalize_site.py` maintains canonical, hreflang, social, favicon, AOS, and footer conventions on legacy pages. It intentionally excludes the generated homepages. `scripts/add_image_dimensions.py` adds intrinsic dimensions to local raster images without reformatting the surrounding HTML.

GitHub Actions repeats link/casing/metadata validation, responsive checks at 390, 820, 1024, and 1440 px, automated accessibility checks, screenshots, and Lighthouse budgets on every pull request.

## Render deployment

The reproducible service definition is in `render.yaml`:

- service type: Static Site
- repository: `MynosIII/WebPage`
- branch: `main`
- build command: `python3 scripts/build_homepages.py --check && python3 scripts/generate_sitemap.py --check && python3 scripts/validate_site.py`
- publish directory: `.`
- auto-deploy: enabled for `main`
- pull-request previews: disabled

The Blueprint also documents the security and cache headers. Render serves the static output through its CDN, forces HTTPS, and atomically invalidates its CDN cache after a successful deploy.

## Asset policy

Commit optimized page images with explicit dimensions and use responsive WebP sources for homepage media. Source documents, spreadsheets, downloaded third-party webpages, and editable production assets belong in the private source archive—not this public deploy repository.

The existing large showcase videos are intentionally unchanged for now because migrating already-published video payloads requires a confirmed object-storage/CDN destination or a coordinated Git LFS rollout. New large binary media should not be added directly to Git history.
