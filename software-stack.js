(async () => {
  const base = document.currentScript?.src ? new URL('.', document.currentScript.src) : new URL('.', location.href);
  const logoPath = file => new URL(`assets/software-logos/${file}`, base).href;
  if (!document.querySelector('link[data-software-stack-styles]')) {
    const stylesheet = document.createElement('link');
    stylesheet.rel = 'stylesheet';
    stylesheet.href = new URL('software-stack.css?v=20260806', base).href;
    stylesheet.dataset.softwareStackStyles = '';
    document.head.append(stylesheet);
  }

  let catalog;
  try {
    const response = await fetch(new URL('content/case-tools.json?v=20260806', base));
    if (!response.ok) throw new Error(`Unable to load case tools (${response.status})`);
    catalog = await response.json();
  } catch (error) {
    console.warn('Case tool metadata is unavailable.', error);
    return;
  }
  const tools = catalog.tools;
  const caseStacks = Object.fromEntries(
    Object.entries(catalog.cases).map(([page, stack]) => [page.toLowerCase(), stack])
  );

  const aboutRows = [
    {
      label: 'Data Analytics',
      slug: 'data',
      direction: 'forward',
      copy: 'Excel avanzado, Google Sheets, SQL, Python, R, Power BI, Tableau, dashboards y automatizaciones internas.',
      copyEn: 'Advanced Excel, Google Sheets, SQL, Python, R, Power BI, Tableau, dashboards and internal automations.',
      tools: ['excel', 'google-sheets', 'sql', 'python', 'r', 'power-bi', 'tableau']
    },
    {
      label: 'Ecommerce',
      slug: 'ecommerce',
      direction: 'reverse',
      copy: 'Amazon Seller Central, Helium 10, Shulex VOC AI, Jungle Scout, Keepa, Sellerboard, Google Ads, Meta Ads, GA4, Search Console, Semrush, Hotjar y Stackline.',
      copyEn: 'Amazon Seller Central, Helium 10, Shulex VOC AI, Jungle Scout, Keepa, Sellerboard, Google Ads, Meta Ads, GA4, Search Console, Semrush, Hotjar and Stackline.',
      tools: ['amazon-seller-central', 'helium10', 'shulex', 'jungle-scout', 'keepa', 'sellerboard', 'google-ads', 'meta-ads', 'ga4', 'search-console', 'semrush', 'hotjar', 'stackline']
    },
    {
      label: 'Creative',
      slug: 'creative',
      direction: 'forward',
      copy: 'Photoshop, Illustrator, Premiere Pro, After Effects, DaVinci Resolve, Blender, Cinema 4D y Nuke.',
      copyEn: 'Photoshop, Illustrator, Premiere Pro, After Effects, DaVinci Resolve, Blender, Cinema 4D and Nuke.',
      tools: ['photoshop', 'illustrator', 'premiere', 'after-effects', 'davinci-resolve', 'blender', 'cinema4d', 'nuke']
    }
  ];
  const caseBackLinks = {
    'animation-01.html': ['creatives.html#video-editing', 'Volver a videos', 'Back to videos'],
    'animation-02.html': ['creatives.html#video-editing', 'Volver a videos', 'Back to videos'],
    'animation-03.html': ['creatives.html#video-editing', 'Volver a videos', 'Back to videos'],
    'animation-04.html': ['creatives.html#video-editing', 'Volver a videos', 'Back to videos'],
    'icon-system-case.html': ['creatives.html#corporate-icon-system', 'Volver a Creatives', 'Back to Creatives'],
    'ecommerce-video-case.html': ['creatives.html#ecommerce-conversion-videos', 'Volver a videos', 'Back to videos'],
    'ecommerce-video-01.html': ['creatives.html#ecommerce-conversion-videos', 'Volver a videos', 'Back to videos'],
    'ecommerce-video-02.html': ['creatives.html#ecommerce-conversion-videos', 'Volver a videos', 'Back to videos'],
    'ecommerce-video-03.html': ['creatives.html#ecommerce-conversion-videos', 'Volver a videos', 'Back to videos'],
    'ecommerce-video-04.html': ['creatives.html#ecommerce-conversion-videos', 'Volver a videos', 'Back to videos'],
    'ecommerce-video-05.html': ['creatives.html#ecommerce-conversion-videos', 'Volver a videos', 'Back to videos'],
    'voice-of-customer-conversion-brief.html': ['../Articles.html', 'Volver a artículos', 'Back to Articles'],
    'shulex-voc-creative-case.html': ['creatives.html#shulex-voc-creative', 'Volver a Creatives', 'Back to Creatives'],
    'market-share-loss-diagnosis.html': ['../Articles.html', 'Volver a artículos', 'Back to Articles'],
    'amazon-listing-audit-checklist.html': ['../Articles.html', 'Volver a artículos', 'Back to Articles'],
    'search-query-keyword-harvesting.html': ['../Articles.html', 'Volver a artículos', 'Back to Articles'],
    'search-suppression-catalog-recovery.html': ['../Articles.html', 'Volver a artículos', 'Back to Articles'],
    'automotive-fitment-seo.html': ['../Articles.html', 'Volver a artículos', 'Back to Articles'],
    'amazon-lifecycle-operating-system.html': ['ecommerce.html#cases', 'Volver a Ecommerce', 'Back to Ecommerce'],
    'amazon-content-architecture.html': ['ecommerce.html#cases', 'Volver a Ecommerce', 'Back to Ecommerce'],
    'unimac-case.html': ['creatives.html#unimac-heater-campaign', 'Volver a Creatives', 'Back to Creatives'],
    'Revolution_creative_case.html': ['creatives.html', 'Volver a Creatives', 'Back to Creatives'],
    'BI-case-2.html': ['ecommerce.html', 'Volver a Ecommerce', 'Back to Ecommerce'],
    'DayParting-Case.html': ['../ecommerce.html', 'Volver a Ecommerce', 'Back to Ecommerce'],
    'caso-daizzy-gear.html': ['ecommerce.html', 'Volver a Ecommerce', 'Back to Ecommerce'],
    'caso-daizzy-gear-en.html': ['ecommerce.html', 'Volver a Ecommerce', 'Back to Ecommerce'],
    'caso-hogar-cocina-ppc.html': ['ecommerce.html', 'Volver a Ecommerce', 'Back to Ecommerce'],
    'caso-1.html': ['ecommerce.html', 'Volver a Ecommerce', 'Back to Ecommerce'],
    'caso-2.html': ['ecommerce.html', 'Volver a Ecommerce', 'Back to Ecommerce'],
    'caso-3.html': ['ecommerce.html', 'Volver a Ecommerce', 'Back to Ecommerce']
  };

  const card = key => {
    const tool = tools[key];
    if (!tool) return '';
    return `<span class="software-logo-card"><img src="${logoPath(tool.asset)}" alt="" aria-hidden="true" data-media-type="software-logo" data-media-description="Logo de ${tool.name}" decoding="async"><b>${tool.name}</b></span>`;
  };
  const compactCard = key => {
    const tool = tools[key];
    if (!tool) return '';
    return `<span class="case-card-tool-badge"><img src="${logoPath(tool.asset)}" alt="" aria-hidden="true" decoding="async"><span>${tool.name}</span></span>`;
  };

  const pageName = decodeURIComponent(location.pathname.split('/').pop() || 'index.html');
  const localeMatch = pageName.match(/-(en|es)\.html$/i);
  const pageLocale = localeMatch?.[1]?.toLowerCase() || '';
  const basePageName = localeMatch ? pageName.replace(/-(en|es)(?=\.html$)/i, '') : pageName;
  const spanishPage = document.documentElement.lang.toLowerCase().startsWith('es');
  const localizedHref = href => {
    if (!pageLocale || !href) return href;
    const [path, hash] = href.split('#');
    const localizedPath = path.replace(/\.html$/i, `-${pageLocale}.html`);
    return `${localizedPath}${hash ? `#${hash}` : ''}`;
  };
  const isAbout = basePageName.toLowerCase() === 'sobre-mi.html';
  const shellClass = document.querySelector('.home-shell') ? 'home-shell' : 'container';

  const cardLinkSelector = [
    '.work-card .text-link[href]',
    '.caso-card-link[href]',
    '.article-card[href]',
    '.video-project[href]',
    '.voc-ai-showcase[href]',
    '.revolution-showcase[href]',
    '.icon-system-showcase[href]',
    '.ecommerce-video-case-link[href]',
    '.flyer-case-link[href]'
  ].join(',');
  document.querySelectorAll(cardLinkSelector).forEach(link => {
    const targetPage = decodeURIComponent(new URL(link.href, location.href).pathname.split('/').pop() || '');
    const targetBase = targetPage.replace(/-(en|es)(?=\.html$)/i, '').toLowerCase();
    const stack = caseStacks[targetBase];
    if (!stack?.length) return;
    const workCard = link.closest('.work-card');
    const target = workCard?.querySelector('.work-card__body')
      || link.querySelector('.caso-contenido, .article-card-body, .voc-ai-showcase-copy, .revolution-showcase-copy, .icon-system-showcase-copy')
      || (link.matches('.ecommerce-video-case-link, .flyer-case-link') ? link.parentElement : link);
    if (!target || target.querySelector(':scope > .case-card-tool-badges')) return;
    const badges = document.createElement('span');
    badges.className = 'case-card-tool-badges';
    badges.setAttribute('aria-label', `${spanishPage ? 'Herramientas usadas' : 'Tools used'}: ${stack.map(key => tools[key]?.name).filter(Boolean).join(', ')}`);
    badges.innerHTML = stack.map(compactCard).join('');
    target.append(badges);
  });

  if (isAbout) {
    const section = document.createElement('section');
    section.className = 'software-marquee-section';
    section.innerHTML = `
      <div class="${shellClass} software-marquee-heading">
        <span>${spanishPage ? 'Herramientas que uso' : 'Tools I use'}</span>
        <h2>${spanishPage ? 'Mi stack de software' : 'My software stack'}</h2>
        <p>${spanishPage ? 'Creatividad, análisis, ecommerce y automatización conectados en un mismo flujo de trabajo.' : 'Creative work, analytics, ecommerce and automation connected in one workflow.'}</p>
      </div>
      ${aboutRows.map(row => `
        <div class="software-marquee-row" data-software-row="${row.slug}">
          <div class="${shellClass} software-marquee-row-label">
            <h3>${row.label}</h3>
            <p>${spanishPage ? row.copy : row.copyEn}</p>
          </div>
          <div class="software-marquee" aria-label="Herramientas de ${row.label}">
            <div class="software-marquee-track ${row.direction === 'forward' ? 'software-marquee-forward' : 'software-marquee-reverse'}">${Array.from({length: 4}, () => row.tools).flat().map(card).join('')}</div>
          </div>
        </div>`).join('')}`;
    const contact = document.getElementById(spanishPage ? 'contacto' : 'contact') || document.querySelector('.contact-band');
    contact?.before(section);
    return;
  }

  const selected = caseStacks[basePageName.toLowerCase()];
  if (!selected?.length) return;
  const spanishCase = spanishPage;
  const baseBackLink = caseBackLinks[pageName] || caseBackLinks[basePageName];
  const backLink = baseBackLink ? [localizedHref(baseBackLink[0]), baseBackLink[1], baseBackLink[2]] : null;
  const contactSubject = encodeURIComponent(spanishCase ? `Consulta sobre ${document.title}` : `Project inquiry — ${document.title}`);
  const section = document.createElement('section');
  section.className = 'case-software-stack';
  section.innerHTML = `<div class="${shellClass}"><div class="case-software-heading"><span>Software stack</span><h2>${spanishCase ? 'Herramientas detrás de este caso' : 'Tools behind this case'}</h2></div><div class="case-software-grid">${selected.map(card).join('')}</div><div class="case-end-actions"><p>${spanishCase ? '¿Querés trabajar conmigo en un proyecto similar?' : 'Want to work together on a similar project?'}</p><a class="case-contact-cta" href="mailto:matiasignaciogaglio@gmail.com?subject=${contactSubject}">${spanishCase ? 'Contactame' : 'Let’s work together'} <span aria-hidden="true">↗</span></a>${backLink ? `<a class="case-back-link" href="${backLink[0]}">← ${spanishCase ? backLink[1] : backLink[2]}</a>` : ''}</div></div>`;
  document.querySelector('main')?.append(section);
})();
