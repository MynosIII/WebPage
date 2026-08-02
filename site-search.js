(() => {
  const script = document.currentScript;
  const baseUrl = new URL('.', script?.src || location.href);
  const lang = document.documentElement.lang?.toLowerCase().startsWith('es') ? 'es' : 'en';
  const labels = lang === 'es'
    ? { button: 'Buscar', placeholder: 'Buscar casos, artículos y páginas…', close: 'Cerrar búsqueda', empty: 'No encontramos resultados.', count: n => `${n} resultado${n === 1 ? '' : 's'}`, all: 'Resultados de búsqueda' }
    : { button: 'Search', placeholder: 'Search cases, articles and pages…', close: 'Close search', empty: 'No results found.', count: n => `${n} result${n === 1 ? '' : 's'}`, all: 'Search results' };

  const ensurePortfolioRail = () => {
    if (document.querySelector('[data-portfolio-rail]')) return;
    const header = document.querySelector('.site-header, .navbar, .document-header');
    if (!header) return;
    const items = lang === 'es'
      ? [
          ['Mapa', 'index.html#trabajo'],
          ['Ecommerce', 'ecommerce-es.html'],
          ['Creatives', 'creatives-es.html'],
          ['Artículos', 'Articles-es.html'],
          ['Investigación de opinión', 'consultora-es.html'],
          ['Otros proyectos', 'otros-es.html'],
          ['Chat Matías', 'SEO-es.html']
        ]
      : [
          ['Map', 'index-en.html#work'],
          ['Ecommerce', 'ecommerce-en.html'],
          ['Creatives', 'creatives-en.html'],
          ['Articles', 'Articles-en.html'],
          ['Opinion research', 'consultora-en.html'],
          ['Other projects', 'otros-en.html'],
          ['Chat Matías', 'SEO-en.html']
        ];
    const rail = document.createElement('nav');
    rail.className = 'portfolio-rail portfolio-rail--global';
    rail.dataset.portfolioRail = '';
    rail.setAttribute('aria-label', lang === 'es' ? 'Accesos al portafolio' : 'Portfolio shortcuts');
    rail.innerHTML = `<div class="portfolio-rail__inner"><div class="portfolio-rail__links">${items.map(([label, path], index) => `<a class="${index === 0 ? 'portfolio-rail__home' : 'portfolio-rail__link'}" href="${new URL(path, baseUrl).href}"><span aria-hidden="true">${String(index).padStart(2, '0')}</span>${label}</a>`).join('')}</div><button class="portfolio-rail__search" type="button" data-search-trigger aria-controls="site-search-panel" aria-expanded="false"><span aria-hidden="true">⌕</span>${labels.button}</button></div>`;
    const backdrop = header.nextElementSibling?.matches('.menu-backdrop, .legacy-nav-backdrop') ? header.nextElementSibling : null;
    (backdrop || header).after(rail);
    document.body.classList.add('has-portfolio-rail');
    if (header.classList.contains('document-header')) document.body.classList.add('has-document-rail');
  };
  ensurePortfolioRail();

  const navbar = document.querySelector('.navbar .container, .site-header__actions, .document-header-inner');
  if (!navbar || document.querySelector('.site-search')) return;
  const externalTriggers = [...document.querySelectorAll('[data-search-trigger]')];

  const normalize = value => (value || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
  const distance = (a, b) => {
    const row = Array.from({ length: b.length + 1 }, (_, i) => i);
    for (let i = 1; i <= a.length; i++) {
      let previous = row[0]; row[0] = i;
      for (let j = 1; j <= b.length; j++) {
        const saved = row[j];
        row[j] = Math.min(row[j] + 1, row[j - 1] + 1, previous + (a[i - 1] === b[j - 1] ? 0 : 1)); previous = saved;
      }
    }
    return row[b.length];
  };
  const isMatch = (token, word) => {
    if (word.includes(token)) return true;
    if (token.length < 3) return false;
    const tolerance = token.length >= 8 ? 2 : 1;
    return Math.abs(word.length - token.length) <= tolerance && distance(token, word) <= tolerance;
  };
  const tokenScore = (token, field, weight) => {
    if (!field) return 0;
    if (field.includes(token)) return weight * (field.startsWith(token) ? 1.25 : 1);
    return field.split(' ').some(word => isMatch(token, word)) ? weight * .72 : 0;
  };
  const score = (page, query) => normalize(query).split(' ').filter(Boolean).reduce((total, token) => total + Math.max(
    tokenScore(token, normalize(page.title), 12), tokenScore(token, normalize(page.keywords), 6),
    tokenScore(token, normalize(page.description), 4), tokenScore(token, normalize(page.content), 1)
  ), 0);
  const escapeHtml = value => value.replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]);
  let currentQuery = '';
  const highlight = value => {
    const tokens = normalize(currentQuery).split(' ').filter(Boolean);
    return escapeHtml(value).replace(/[\p{L}\p{N}]+/gu, word => tokens.some(token => isMatch(token, normalize(word))) ? `<strong>${word}</strong>` : word);
  };
  const snippet = page => {
    const source = page.content || page.description || '';
    const tokens = normalize(currentQuery).split(' ').filter(Boolean);
    const words = [...source.matchAll(/[\p{L}\p{N}]+/gu)];
    const matched = new Set(); let position = -1;
    words.forEach(word => { const value = normalize(word[0]); if (tokens.some(token => isMatch(token, value))) { matched.add(value); if (position < 0) position = word.index; } });
    const start = Math.max(0, position < 0 ? 0 : position - 80);
    const excerpt = source.slice(start, start + 220).trim();
    const highlighted = escapeHtml(excerpt).replace(/[\p{L}\p{N}]+/gu, word => matched.has(normalize(word)) ? `<strong>${word}</strong>` : word);
    return `${start ? '…' : ''}${highlighted}${source.length > start + 220 ? '…' : ''}`;
  };
  const imageUrl = page => page.image ? new URL(page.image, new URL(page.url, baseUrl)).href : '';
  const resultMarkup = page => `<a role="option" class="site-search-result" href="${new URL(page.url, baseUrl).href}"><span class="site-search-result-copy"><span class="site-search-result-title">${highlight(page.title)}</span><span>${snippet(page)}</span></span>${page.image ? `<img src="${escapeHtml(imageUrl(page))}" alt="" loading="lazy">` : '<span class="site-search-result-placeholder" aria-hidden="true"></span>'}</a>`;

  const shell = document.createElement('div');
  shell.className = 'site-search';
  shell.innerHTML = `<button class="site-search-toggle" type="button" aria-label="${labels.button}" aria-controls="site-search-panel" aria-expanded="false"><span aria-hidden="true">⌕</span><span class="site-search-label">${labels.button}</span></button><div class="site-search-panel" id="site-search-panel" hidden><div class="site-search-field"><span aria-hidden="true">⌕</span><input type="search" autocomplete="off" spellcheck="false" placeholder="${labels.placeholder}" aria-label="${labels.placeholder}" aria-controls="site-search-results"><button type="button" class="site-search-close" aria-label="${labels.close}">×</button></div><div class="site-search-status" aria-live="polite"></div><div class="site-search-results" id="site-search-results" role="listbox"></div></div>`;
  navbar.insertBefore(shell, navbar.querySelector('.nav-toggle, .menu-button'));
  const toggle = shell.querySelector('.site-search-toggle'), panel = shell.querySelector('.site-search-panel'), input = shell.querySelector('input'), close = shell.querySelector('.site-search-close'), status = shell.querySelector('.site-search-status'), results = shell.querySelector('.site-search-results');
  const fullResults = document.querySelector('[data-search-page-results]'), fullStatus = document.querySelector('[data-search-page-status]');
  let pages = [];
  const find = (query, limit) => pages.map(page => ({ page, score: score(page, query) })).filter(item => item.score > 0).sort((a, b) => b.score - a.score).slice(0, limit);
  const renderFullPage = () => {
    if (!fullResults) return;
    currentQuery = new URLSearchParams(location.search).get('q')?.trim() || '';
    input.value = currentQuery;
    const heading = document.querySelector('[data-search-page-heading]');
    if (heading) heading.textContent = currentQuery ? `${labels.all}: “${currentQuery}”` : labels.all;
    if (!currentQuery) return;
    const matches = find(currentQuery, pages.length);
    fullStatus.textContent = matches.length ? labels.count(matches.length) : labels.empty;
    fullResults.innerHTML = matches.map(({ page }) => resultMarkup(page)).join('');
  };
  fetch(new URL('search-index.json', baseUrl)).then(response => response.ok ? response.json() : Promise.reject()).then(data => { pages = data.filter(page => page.lang === lang); renderFullPage(); }).catch(() => { status.textContent = labels.empty; if (fullStatus) fullStatus.textContent = labels.empty; });
  let restoreTarget = toggle;
  const setOpen = (open, trigger = restoreTarget) => { panel.hidden = !open; toggle.setAttribute('aria-expanded', String(open)); externalTriggers.forEach(item => item.setAttribute('aria-expanded', String(open))); document.body.classList.toggle('site-search-open', open); if (open) { restoreTarget = trigger; input.focus(); } };
  toggle.addEventListener('click', () => setOpen(panel.hidden, toggle));
  externalTriggers.forEach(trigger => { trigger.setAttribute('aria-expanded', 'false'); trigger.addEventListener('click', () => setOpen(true, trigger)); });
  close.addEventListener('click', () => { setOpen(false); restoreTarget?.focus(); });
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && !panel.hidden) { setOpen(false); restoreTarget?.focus(); } });
  input.addEventListener('input', () => { currentQuery = input.value.trim(); if (!currentQuery) { status.textContent = ''; results.innerHTML = ''; return; } const matches = find(currentQuery, 10); status.textContent = matches.length ? labels.count(matches.length) : labels.empty; results.innerHTML = matches.map(({ page }) => resultMarkup(page)).join(''); });
  input.addEventListener('keydown', event => { if (event.key === 'Enter' && input.value.trim()) { event.preventDefault(); location.href = new URL(`search-${lang}.html?q=${encodeURIComponent(input.value.trim())}`, baseUrl).href; } });
})();
