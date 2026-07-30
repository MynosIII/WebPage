(() => {
  const base = document.currentScript?.src ? new URL('.', document.currentScript.src) : new URL('.', location.href);
  const logoPath = file => new URL(`assets/software-logos/${file}`, base).href;

  const tools = {
    photoshop: ['Photoshop', 'photoshop.svg'],
    'after-effects': ['After Effects', 'after-effects.svg'],
    illustrator: ['Illustrator', 'illustrator.svg'],
    premiere: ['Premiere Pro', 'premiere.svg'],
    excel: ['Excel', 'excel.svg'],
    'google-sheets': ['Google Sheets', 'google-sheets.svg'],
    python: ['Python', 'python.svg'],
    'power-bi': ['Power BI', 'power-bi.svg'],
    'davinci-resolve': ['DaVinci Resolve', 'davinci-resolve.svg'],
    blender: ['Blender', 'blender.svg'],
    helium10: ['Helium 10', 'helium10.svg'],
    'jungle-scout': ['Jungle Scout', 'jungle-scout.svg'],
    keepa: ['Keepa', 'keepa.svg'],
    sellerboard: ['Sellerboard', 'sellerboard.svg'],
    'amazon-seller-central': ['Amazon Seller Central', 'amazon-seller-central.svg'],
    'google-ads': ['Google Ads', 'google-ads.svg'],
    'meta-ads': ['Meta Ads', 'meta-ads.svg'],
    ga4: ['Google Analytics 4', 'ga4.svg'],
    'search-console': ['Search Console', 'search-console.svg'],
    semrush: ['Semrush', 'semrush.svg'],
    sql: ['SQL', 'sql.svg'],
    hotjar: ['Hotjar', 'hotjar.svg'],
    tableau: ['Tableau', 'tableau.svg'],
    r: ['R', 'r.svg'],
    stackline: ['Stackline', 'stackline.svg']
  };

  const aboutRows = [
    {
      label: 'Data',
      copy: 'Excel avanzado, Google Sheets, SQL, Python, R, Power BI, Tableau, dashboards y automatizaciones internas.',
      tools: ['excel', 'google-sheets', 'sql', 'python', 'r', 'power-bi', 'tableau']
    },
    {
      label: 'Ecommerce',
      copy: 'Amazon Seller Central, Helium 10, Jungle Scout, Keepa, Sellerboard, Google Ads, Meta Ads, GA4, Search Console, Semrush, Hotjar y Stackline.',
      tools: ['amazon-seller-central', 'helium10', 'jungle-scout', 'keepa', 'sellerboard', 'google-ads', 'meta-ads', 'ga4', 'search-console', 'semrush', 'hotjar', 'stackline']
    },
    {
      label: 'Creative',
      copy: 'Photoshop, Illustrator, Premiere Pro, After Effects, DaVinci Resolve y Blender.',
      tools: ['photoshop', 'illustrator', 'premiere', 'after-effects', 'davinci-resolve', 'blender']
    }
  ];
  const caseStacks = {
    'animation-01.html': ['after-effects'],
    'animation-02.html': ['after-effects'],
    'animation-03.html': ['after-effects'],
    'animation-04.html': ['after-effects'],
    'icon-system-case.html': ['illustrator'],
    'ecommerce-video-case.html': ['premiere', 'after-effects', 'amazon-seller-central'],
    'ecommerce-video-01.html': ['premiere', 'after-effects'],
    'ecommerce-video-02.html': ['premiere', 'after-effects'],
    'ecommerce-video-03.html': ['premiere', 'after-effects'],
    'ecommerce-video-04.html': ['premiere', 'after-effects'],
    'ecommerce-video-05.html': ['premiere', 'after-effects'],
    'voice-of-customer-conversion-brief.html': ['excel', 'amazon-seller-central', 'helium10'],
    'market-share-loss-diagnosis.html': ['amazon-seller-central', 'excel', 'stackline'],
    'amazon-listing-audit-checklist.html': ['amazon-seller-central', 'helium10', 'excel'],
    'search-query-keyword-harvesting.html': ['amazon-seller-central', 'excel', 'helium10'],
    'amazon-lifecycle-operating-system.html': ['amazon-seller-central', 'excel', 'helium10', 'semrush'],
    'amazon-content-architecture.html': ['amazon-seller-central', 'helium10', 'photoshop', 'after-effects'],
    'unimac-case.html': ['photoshop', 'illustrator'],
    'Revolution_creative_case.html': ['photoshop', 'amazon-seller-central'],
    'BI-case-2.html': ['amazon-seller-central', 'excel', 'stackline'],
    'DayParting-Case.html': ['amazon-seller-central', 'excel'],
    'caso-daizzy-gear.html': ['amazon-seller-central'],
    'caso-daizzy-gear-en.html': ['amazon-seller-central'],
    'caso-hogar-cocina-ppc.html': ['amazon-seller-central'],
    'caso-1.html': ['amazon-seller-central'],
    'caso-2.html': ['excel'],
    'caso-3.html': ['photoshop']
  };
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
    'market-share-loss-diagnosis.html': ['../Articles.html', 'Volver a artículos', 'Back to Articles'],
    'amazon-listing-audit-checklist.html': ['../Articles.html', 'Volver a artículos', 'Back to Articles'],
    'search-query-keyword-harvesting.html': ['../Articles.html', 'Volver a artículos', 'Back to Articles'],
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
    const [name, file] = tools[key];
    return `<span class="software-logo-card"><img src="${logoPath(file)}" alt="" aria-hidden="true" data-media-type="software-logo" data-media-description="Logo de ${name}" decoding="async"><b>${name}</b></span>`;
  };

  const pageName = decodeURIComponent(location.pathname.split('/').pop() || 'index.html');
  const isAbout = pageName.toLowerCase() === 'sobre-mi.html';

  if (isAbout) {
    const section = document.createElement('section');
    section.className = 'software-marquee-section';
    section.innerHTML = `
      <div class="container software-marquee-heading">
        <span>Herramientas que uso</span>
        <h2>Mi stack de software</h2>
        <p>Creatividad, análisis, ecommerce y automatización conectados en un mismo flujo de trabajo.</p>
      </div>
      ${aboutRows.map((row, index) => `
        <div class="software-marquee-row">
          <div class="container software-marquee-row-label">
            <h3>${row.label}</h3>
            <p>${row.copy}</p>
          </div>
          <div class="software-marquee" aria-label="Herramientas de ${row.label}">
            <div class="software-marquee-track ${index % 2 ? 'software-marquee-forward' : 'software-marquee-reverse'}">${[...row.tools,...row.tools].map(card).join('')}</div>
          </div>
        </div>`).join('')}`;
    const contact = document.getElementById('contacto');
    contact?.before(section);
    return;
  }

  const selected = caseStacks[pageName];
  if (!selected?.length) return;
  const spanishCase = document.documentElement.lang.toLowerCase().startsWith('es');
  const backLink = caseBackLinks[pageName];
  const contactSubject = encodeURIComponent(spanishCase ? `Consulta sobre ${document.title}` : `Project inquiry — ${document.title}`);
  const section = document.createElement('section');
  section.className = 'case-software-stack';
  section.innerHTML = `<div class="container"><div class="case-software-heading"><span>Software stack</span><h2>${spanishCase ? 'Herramientas detrás de este caso' : 'Tools behind this case'}</h2></div><div class="case-software-grid">${selected.map(card).join('')}</div><div class="case-end-actions"><p>${spanishCase ? '¿Querés trabajar conmigo en un proyecto similar?' : 'Want to work together on a similar project?'}</p><a class="case-contact-cta" href="mailto:matiasignaciogaglio@gmail.com?subject=${contactSubject}">${spanishCase ? 'Contactame' : 'Let’s work together'} <span aria-hidden="true">↗</span></a>${backLink ? `<a class="case-back-link" href="${backLink[0]}">← ${spanishCase ? backLink[1] : backLink[2]}</a>` : ''}</div></div>`;
  document.querySelector('main')?.append(section);
})();
