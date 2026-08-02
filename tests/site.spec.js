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

    const menuButton = page.locator('[data-menu-button]');
    if (viewport.width <= 1050) {
      await expect(menuButton).toBeVisible();
      await menuButton.click();
      await expect(menuButton).toHaveAttribute('aria-expanded', 'true');
      await expect(page.locator('main')).toHaveJSProperty('inert', true);
      await expect(page.locator('[data-portfolio-rail]')).toHaveJSProperty('inert', true);
      await page.keyboard.press('Escape');
      await expect(menuButton).toHaveAttribute('aria-expanded', 'false');
      await expect(menuButton).toBeFocused();
    } else {
      await expect(menuButton).toBeHidden();
      await expect(page.locator('[data-site-nav]')).toBeVisible();
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
  await expect(page.locator('.library-card')).toHaveCount(6);
  await expect(page.locator('.portfolio-rail__link')).toHaveCount(6);
  await expect(page.locator('.portfolio-search')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Datos, pauta y contenido al servicio de la rentabilidad.' })).toBeVisible();
  const resumeResponse = await request.get('/output/pdf/Matias-Gaglio-CV-ES.pdf');
  expect(resumeResponse.ok()).toBeTruthy();
  expect(resumeResponse.headers()['content-type']).toContain('application/pdf');
});

test('analytical translator and portfolio search are interactive', async ({ page }) => {
  await page.goto('/index.html', { waitUntil: 'networkidle' });
  const dataNode = page.locator('[data-neural-node="data"]');
  await expect(page.locator('[data-neural-node]')).toHaveCount(3);
  await dataNode.click();
  await expect(dataNode).toHaveAttribute('aria-pressed', 'true');
  await expect(page.locator('[data-neural-output]')).toHaveText('SEÑAL');

  const railSearch = page.locator('[data-search-trigger]');
  await railSearch.click();
  await expect(railSearch).toHaveAttribute('aria-expanded', 'true');
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
    await expect(page.locator('[data-portfolio-rail]')).toBeVisible();
  });
}

test('legacy navigation uses the tablet drawer without clipping', async ({ page }) => {
  await page.setViewportSize({ width: 820, height: 1180 });
  await page.goto('/BI-case-2-es.html', { waitUntil: 'networkidle' });
  const portfolioRail = page.locator('[data-portfolio-rail]');
  await expect(portfolioRail).toBeVisible();
  await expect(portfolioRail.locator('.portfolio-rail__link')).toHaveCount(6);
  await expect(portfolioRail.getByRole('link', { name: 'Investigación de opinión' })).toHaveAttribute('href', /consultora-es\.html$/);
  const menuButton = page.locator('.nav-toggle');
  await expect(menuButton).toBeVisible();
  await menuButton.click();
  await expect(menuButton).toHaveAttribute('aria-expanded', 'true');
  await expect(portfolioRail).toHaveJSProperty('inert', true);
  await expect(page.locator('.nav-menu a[href="sobre-mi-es.html"]')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(menuButton).toHaveAttribute('aria-expanded', 'false');
  await expect(menuButton).toBeFocused();
});

test('site-wide portfolio rail is correctly localized in English', async ({ page }) => {
  await page.goto('/BI-case-2-en.html', { waitUntil: 'networkidle' });
  const portfolioRail = page.locator('[data-portfolio-rail]');
  await expect(portfolioRail).toHaveAttribute('aria-label', 'Portfolio shortcuts');
  await expect(portfolioRail.getByRole('link', { name: 'Opinion research' })).toHaveAttribute('href', /consultora-en\.html$/);
  await expect(portfolioRail.getByRole('button', { name: 'Search' })).toBeVisible();
});

test('site-wide portfolio rail also covers the custom academic article layout', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/articulo-milei-chad.html', { waitUntil: 'networkidle' });
  await expect(page.locator('[data-portfolio-rail]')).toBeVisible();
  await expect(page.locator('.site-search-panel')).toBeAttached();
  const overflow = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth }));
  expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth + 1);
});
