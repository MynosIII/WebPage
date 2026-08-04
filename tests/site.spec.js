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
  await expect(page.locator('.contact-email a')).toHaveText('matiasignaciogaglio@gmail.com');
  await expect(page.getByRole('heading', { name: 'Datos, pauta y contenido al servicio de la rentabilidad.' })).toBeVisible();
  const resumeResponse = await request.get('/output/pdf/Matias-Gaglio-CV-ES.pdf');
  expect(resumeResponse.ok()).toBeTruthy();
  expect(resumeResponse.headers()['content-type']).toContain('application/pdf');
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

for (const path of ['/caso-1-es.html', '/caso-2-es.html', '/caso-3-es.html', '/caso-daizzy-gear-es.html', '/sobre-mi-es.html']) {
  test(`${path} has no mobile overflow or broken images`, async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(path, { waitUntil: 'networkidle' });
    const overflow = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth }));
    expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth + 1);
    const images = await page.locator('img').all();
    for (const image of images) {
      await image.scrollIntoViewIfNeeded();
      await expect(image).toHaveJSProperty('complete', true);
    }
    const brokenImages = await page.locator('img').evaluateAll(images => images.filter(image => !image.complete || image.naturalWidth === 0).length);
    expect(brokenImages).toBe(0);
    await expect(page.locator('[data-global-nav]')).toBeVisible();
    await expect(page.locator('[data-portfolio-rail]')).toHaveCount(0);
  });
}

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
