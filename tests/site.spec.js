const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

const viewports = [
  { name: 'mobile-390', width: 390, height: 844 },
  { name: 'tablet-820', width: 820, height: 1180 },
  { name: 'tablet-1024', width: 1024, height: 768 },
  { name: 'desktop-1440', width: 1440, height: 1000 }
];

for (const viewport of viewports) {
  test(`homepage is stable at ${viewport.name}`, async ({ page }, testInfo) => {
    await page.setViewportSize(viewport);
    await page.goto('/index.html', { waitUntil: 'networkidle' });

    const overflow = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth
    }));
    expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth + 1);

    const images = await page.locator('img').all();
    for (const image of images) {
      await image.scrollIntoViewIfNeeded();
      await expect(image).toHaveJSProperty('complete', true);
      expect(await image.evaluate(element => element.naturalWidth)).toBeGreaterThan(0);
    }

    const menuButton = page.locator('[data-global-nav-toggle]');
    if (viewport.width <= 1040) {
      await expect(menuButton).toBeVisible();
      await menuButton.click();
      await expect(menuButton).toHaveAttribute('aria-expanded', 'true');
      await expect(menuButton).toHaveAttribute('aria-label', 'Cerrar men\u00fa');
      await expect(page.locator('main')).toHaveJSProperty('inert', true);
      await page.keyboard.press('Escape');
      await expect(menuButton).toHaveAttribute('aria-expanded', 'false');
      await expect(menuButton).toHaveAttribute('aria-label', 'Abrir men\u00fa');
      await expect(menuButton).toBeFocused();
    } else {
      await expect(menuButton).toBeHidden();
      await expect(page.locator('[data-global-nav-menu]')).toBeVisible();
    }

    await page.screenshot({
      path: testInfo.outputPath(`homepage-${viewport.name}.png`),
      fullPage: true
    });
  });
}

test('homepage has no serious or critical automated accessibility violations', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto('/index.html', { waitUntil: 'networkidle' });
  const results = await new AxeBuilder({ page }).analyze();
  const blocking = results.violations.filter(violation => ['serious', 'critical'].includes(violation.impact));
  expect(blocking).toEqual([]);
});

test('homepage presents exactly three flagship cases and working recruiter links', async ({ page, request }) => {
  await page.goto('/index.html', { waitUntil: 'networkidle' });
  await expect(page.locator('.work-card')).toHaveCount(3);
  await expect(page.locator('.library-card')).toHaveCount(0);
  await expect(page.locator('[data-portfolio-rail]')).toHaveCount(0);
  await expect(page.locator('.portfolio-search')).toHaveCount(0);
  await expect(page.locator('.proof-item')).toHaveCount(4);
  await expect(page.locator('.contact-action__email')).toHaveText('matiasignaciogaglio@gmail.com');
  await expect(page.getByRole('heading', { name: 'Datos, pauta y contenido al servicio de la rentabilidad.' })).toBeVisible();
  const resumeResponse = await request.get('/output/pdf/Matias-Gaglio-CV-ES.pdf');
  expect(resumeResponse.ok()).toBeTruthy();
  expect(resumeResponse.headers()['content-type']).toContain('application/pdf');
});

test('homepage case metrics stay compact on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/index-es.html', { waitUntil: 'networkidle' });

  const metrics = page.locator('.work-card__metrics').first();
  await expect(metrics.locator('li')).toHaveCount(3);
  const layout = await metrics.evaluate(element => ({
    height: Math.round(element.getBoundingClientRect().height),
    items: [...element.children].map(item => ({
      borderRadius: getComputedStyle(item).borderRadius,
      backgroundColor: getComputedStyle(item).backgroundColor
    }))
  }));

  expect(layout.height).toBeLessThan(105);
  expect(layout.items.every(item => item.borderRadius === '0px')).toBe(true);
  expect(layout.items.every(item => item.backgroundColor === 'rgba(0, 0, 0, 0)')).toBe(true);
});

test('contact CTAs expand into email and copy actions', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto('/index-es.html', { waitUntil: 'networkidle' });

  const action = page.locator('.contact-action').first();
  const mail = action.locator('.contact-action__mail');
  const copy = action.locator('.contact-action__copy');
  await expect(action).toHaveCount(1);
  await expect(mail).toHaveAttribute('aria-label', 'Enviar email a matiasignaciogaglio@gmail.com');
  const collapsedWidth = await action.evaluate(element => Math.round(element.getBoundingClientRect().width));

  await action.hover();
  await expect(mail).toHaveAttribute('aria-expanded', 'true');
  await expect(action.locator('.contact-action__email')).toHaveText('matiasignaciogaglio@gmail.com');
  await expect(copy).toBeVisible();
  await expect.poll(() => action.evaluate(element => Math.round(element.getBoundingClientRect().width))).toBeGreaterThan(collapsedWidth);

  await copy.click();
  await expect(copy).toContainText('Copiado');
});

test('contact CTA opens safely on touch before launching email', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/sobre-mi-es.html', { waitUntil: 'networkidle' });
  const action = page.locator('.contact-action').first();
  const mail = action.locator('.contact-action__mail');
  const startingUrl = page.url();

  await mail.click();
  await expect(mail).toHaveAttribute('aria-expanded', 'true');
  await expect(action.locator('.contact-action__copy')).toBeVisible();
  expect(page.url()).toBe(startingUrl);
});

test('homepage and About route resume viewers to the interactive CV', async ({ page }) => {
  await page.goto('/index-es.html', { waitUntil: 'networkidle' });
  const homeResume = page.locator('.hero-cv-link');
  await expect(homeResume).toHaveText(/Ver CV/);
  await expect(homeResume).toHaveAttribute('href', 'cv-es.html');
  await expect(homeResume).not.toHaveAttribute('download', '');

  await page.goto('/sobre-mi-es.html', { waitUntil: 'networkidle' });
  const aboutResume = page.locator('.about-story-hero .button--primary');
  await expect(aboutResume).toHaveText('Ver CV');
  await expect(aboutResume).toHaveAttribute('href', 'cv-es.html');
});

test('interactive CV exposes evidence, navigation and PDF download', async ({ page, request }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto('/cv-es.html', { waitUntil: 'networkidle' });
  await expect(page.getByRole('heading', { name: 'Matías Gaglio.' })).toBeVisible();
  await expect(page.locator('[data-cv-section]')).toHaveCount(5);
  await expect(page.locator('.cv-case')).toHaveCount(3);
  await expect(page.locator('.cv-case[open]')).toHaveCount(1);
  await expect(page.locator('.cv-skill-group')).toHaveCount(3);

  const expand = page.locator('[data-cv-expand]');
  await expand.click();
  await expect(page.locator('.cv-case[open]')).toHaveCount(3);
  await expect(expand).toHaveText('Cerrar todos');
  await expand.click();
  await expect(page.locator('.cv-case[open]')).toHaveCount(0);

  const download = page.getByRole('link', { name: /Descargar PDF/ });
  await expect(download).toHaveAttribute('href', 'output/pdf/Matias-Gaglio-CV-ES.pdf');
  await expect(download).toHaveAttribute('download', '');
  const response = await request.get('/output/pdf/Matias-Gaglio-CV-ES.pdf');
  expect(response.ok()).toBeTruthy();
  expect(response.headers()['content-type']).toContain('application/pdf');
});

test('interactive CV is localized and accessible', async ({ page }) => {
  await page.goto('/cv-en.html', { waitUntil: 'networkidle' });
  await expect(page.getByText('Interactive resume · Professional profile')).toBeVisible();
  await expect(page.getByRole('link', { name: /Download PDF/ })).toHaveAttribute('href', 'output/pdf/Matias-Gaglio-Resume-EN.pdf');
  const results = await new AxeBuilder({ page }).analyze();
  const blocking = results.violations.filter(violation => ['serious', 'critical'].includes(violation.impact));
  expect(blocking).toEqual([]);
});

test('featured cases precede the compact analytical translator and the single search remains interactive', async ({ page }) => {
  await page.goto('/index.html', { waitUntil: 'networkidle' });
  await expect(page.locator('.translator-steps li')).toHaveCount(3);
  const positions = await page.evaluate(() => ({
    cases: document.querySelector('.selected-work').getBoundingClientRect().top + scrollY,
    translator: document.querySelector('.translator-band').getBoundingClientRect().top + scrollY,
    capabilities: document.querySelector('.capabilities').getBoundingClientRect().top + scrollY
  }));
  expect(positions.cases).toBeLessThan(positions.translator);
  expect(positions.translator).toBeLessThan(positions.capabilities);

  const searchToggle = page.locator('.site-search-toggle');
  await searchToggle.click();
  await expect(searchToggle).toHaveAttribute('aria-expanded', 'true');
  await expect(page.locator('.site-search-panel')).toBeVisible();
  await expect(page.locator('.site-search-field input')).toBeFocused();
});

for (const path of ['/caso-1-es.html', '/caso-2-es.html', '/caso-3-es.html', '/caso-daizzy-gear-es.html', '/sobre-mi-es.html', '/cv-es.html']) {
  test(`${path} has no mobile overflow or broken images`, async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(path, { waitUntil: 'networkidle' });
    const overflow = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth }));
    expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth + 1);
    const images = await page.locator('img:not([data-media-type="software-logo"])').all();
    for (const image of images) {
      await image.scrollIntoViewIfNeeded();
      await expect(image).toHaveJSProperty('complete', true);
    }
    const softwareLogos = page.locator('img[data-media-type="software-logo"]');
    await expect.poll(() => softwareLogos.evaluateAll(images => images.filter(image => !image.complete || image.naturalWidth === 0).length)).toBe(0);
    const brokenImages = await page.locator('img').evaluateAll(images => images.filter(image => !image.complete || image.naturalWidth === 0).length);
    expect(brokenImages).toBe(0);
    await expect(page.locator('[data-global-nav]')).toBeVisible();
    await expect(page.locator('[data-portfolio-rail]')).toHaveCount(0);
  });
}

test('about profile details are visible by default and remain collapsible', async ({ page }) => {
  await page.goto('/sobre-mi-es.html', { waitUntil: 'networkidle' });
  const disclosure = page.locator('.tools-disclosure');
  await expect(disclosure).toHaveAttribute('open', '');
  await expect(disclosure.getByText('Seller Central y Amazon Ads')).toBeVisible();
  await expect(page.locator('.software-marquee-section')).toBeVisible();
  await expect(page.locator('.software-marquee-row')).toHaveCount(3);
  await expect(page.locator('[data-software-row="ecommerce"] .software-logo-card').filter({ hasText: 'Amazon Seller Central' })).not.toHaveCount(0);
  await disclosure.locator('summary').click();
  await expect(disclosure).not.toHaveAttribute('open', '');
});

test('case tools appear on listing cards and at the end of each case', async ({ page }) => {
  await page.goto('/ecommerce-es.html', { waitUntil: 'networkidle' });
  const card = page.locator('a.caso-card-link[href="amazon-content-architecture-es.html"]');
  await expect(card.locator('.case-card-tool-badges')).toBeVisible();
  await expect(card.locator('.case-card-tool-badge')).toHaveCount(4);
  await expect(card.getByText('Photoshop', { exact: true })).toBeVisible();
  const sellerboardCard = page.locator('a.caso-card-link[href="caso-2-es.html"]');
  await expect(sellerboardCard.getByText('Sellerboard', { exact: true })).toBeVisible();

  await page.goto('/caso-1-es.html', { waitUntil: 'networkidle' });
  await expect(page.locator('.case-software-stack')).toBeVisible();
  await expect(page.locator('.case-software-stack').getByText('Amazon Seller Central', { exact: true })).toBeVisible();
  await expect(page.locator('.case-software-stack').getByText('Amazon Ads', { exact: true })).toBeVisible();
  await expect(page.locator('.case-software-stack .contact-action')).toBeVisible();

  await page.goto('/caso-2-es.html', { waitUntil: 'networkidle' });
  await expect(page.locator('.case-software-stack').getByText('Sellerboard', { exact: true })).toBeVisible();
});

test('case software is indexed as backend search keywords', async ({ request }) => {
  const response = await request.get('/search-index.json');
  expect(response.ok()).toBeTruthy();
  const index = await response.json();
  const casePage = index.find(item => item.url === 'amazon-content-architecture-es.html');
  expect(casePage.tools).toEqual(expect.arrayContaining(['Amazon Seller Central', 'Helium 10', 'Photoshop', 'After Effects']));
  expect(casePage.keywords).toContain('Photoshop');
  const ppcCase = index.find(item => item.url === 'caso-1-es.html');
  expect(ppcCase.tools).toEqual(expect.arrayContaining(['Amazon Seller Central', 'Amazon Ads']));
  expect(ppcCase.keywords).toContain('Amazon Ads');
  const sellerboardCase = index.find(item => item.url === 'caso-2-es.html');
  expect(sellerboardCase.tools).toContain('Sellerboard');
  expect(sellerboardCase.keywords).toContain('Sellerboard');
});

test('shared navigation uses the tablet drawer without clipping', async ({ page }) => {
  await page.setViewportSize({ width: 820, height: 1180 });
  await page.goto('/BI-case-2-es.html', { waitUntil: 'networkidle' });
  await expect(page.locator('[data-portfolio-rail]')).toHaveCount(0);
  const menuButton = page.locator('[data-global-nav-toggle]');
  await expect(menuButton).toBeVisible();
  await menuButton.click();
  await expect(menuButton).toHaveAttribute('aria-expanded', 'true');
  await expect(page.locator('main')).toHaveJSProperty('inert', true);
  await expect(page.locator('[data-global-nav-menu] a[href="sobre-mi-es.html"]')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(menuButton).toHaveAttribute('aria-expanded', 'false');
  await expect(menuButton).toBeFocused();
});

test('site-wide shared navigation is correctly localized in English', async ({ page }) => {
  await page.goto('/BI-case-2-en.html', { waitUntil: 'networkidle' });
  const sharedNav = page.locator('[data-global-nav-menu]');
  await expect(sharedNav).toHaveAttribute('aria-label', 'Main navigation');
  await expect(sharedNav.getByRole('link', { name: 'Opinion Consultancy' })).toHaveAttribute('href', /consultora-en\.html$/);
  await expect(page.locator('.site-search-toggle')).toBeVisible();
});

test('site-wide shared navigation also covers the custom academic article layout', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/articulo-milei-chad.html', { waitUntil: 'networkidle' });
  await expect(page.locator('[data-global-nav]')).toBeVisible();
  await expect(page.locator('[data-portfolio-rail]')).toHaveCount(0);
  await expect(page.locator('.site-search-panel')).toBeAttached();
  const overflow = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth }));
  expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth + 1);
});
