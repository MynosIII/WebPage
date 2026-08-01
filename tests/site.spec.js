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

test('legacy navigation uses the tablet drawer without clipping', async ({ page }) => {
  await page.setViewportSize({ width: 820, height: 1180 });
  await page.goto('/BI-case-2-es.html', { waitUntil: 'networkidle' });
  const menuButton = page.locator('.nav-toggle');
  await expect(menuButton).toBeVisible();
  await menuButton.click();
  await expect(menuButton).toHaveAttribute('aria-expanded', 'true');
  await expect(page.locator('.nav-menu a[href="sobre-mi-es.html"]')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(menuButton).toHaveAttribute('aria-expanded', 'false');
  await expect(menuButton).toBeFocused();
});
