// Run with Playwright CLI's run-code --filename on a local Jekyll preview.
// All browser navigation stays on localhost, including the destination fixture.
async page => {
  const origin = new URL(page.url()).origin;
  if (!['localhost', '127.0.0.1'].includes(new URL(origin).hostname)) {
    throw new Error('Browser checks require a localhost preview');
  }
  const router = `${origin}/personal-website-router/`;
  const target = `${origin}/router-test-destination`;
  const start = `${origin}/router-test-start`;
  const response = await page.request.get(router);
  if (!response.ok()) throw new Error(`Preview returned ${response.status()}`);
  const source = await response.text();
  const fixture = source
    .replace(/(<meta http-equiv="refresh" content=")0; url=[^"]+"/, `$10; url=${target}"`)
    .replace(/window\.location\.replace\([^\n]+\);/, `window.location.replace(${JSON.stringify(target)});`)
    .replace(/(<a href=")[^"]+"/, `$1${target}"`);
  const browser = page.context().browser();
  const assert = (condition, message) => { if (!condition) throw new Error(message); };
  const results = [];

  for (const javaScriptEnabled of [true, false]) {
    const context = await browser.newContext({ javaScriptEnabled, reducedMotion: 'reduce' });
    const errors = [];
    const tab = await context.newPage();
    tab.on('pageerror', error => errors.push(error.message));
    await context.route(`${origin}/**`, route => {
      const url = route.request().url();
      const body = url === target ? '<!doctype html><title>Local destination</title><h1>Local destination</h1>'
        : url === start ? '<!doctype html><title>Router start</title><a href="/personal-website-router/">Open router</a>'
        : fixture;
      return route.fulfill({ status: 200, contentType: 'text/html', body });
    });
    try {
      for (const width of [390, 1440]) {
        await tab.setViewportSize({ width, height: width === 390 ? 844 : 900 });
        await tab.goto(start);
        await tab.getByRole('link', { name: 'Open router' }).click();
        await tab.waitForURL(target);
        assert(await tab.getByRole('heading', { name: 'Local destination' }).isVisible(), 'Redirect did not arrive');
        if (javaScriptEnabled) {
          await tab.goBack();
          assert(tab.url() === start, 'Back button returned to router');
        }
        results.push(`PASS immediate redirect: ${width}px, JavaScript ${javaScriptEnabled}`);
      }

      // Block only the two automatic mechanisms to inspect and click the real fallback.
      const fallback = fixture
        .replace(/<meta http-equiv="refresh"[^>]*>/, '')
        .replace(/<script>\s*window\.location\.replace\([^\n]+\);\s*<\/script>/, '');
      await context.unroute(`${origin}/**`);
      await context.route(router, route => route.fulfill({ status: 200, contentType: 'text/html', body: fallback }));
      await context.route(target, route => route.fulfill({ status: 200, contentType: 'text/html', body: '<h1>Local destination</h1>' }));
      for (const width of [390, 1440]) {
        await tab.setViewportSize({ width, height: width === 390 ? 844 : 900 });
        await tab.goto(router);
        const link = tab.getByRole('link', { name: 'Continue to my website' });
        const bounds = await link.boundingBox();
        assert(bounds.height >= 44, 'Fallback touch target is too small');
        assert(await tab.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Horizontal overflow');
        await tab.keyboard.press('Tab');
        assert(await link.evaluate(element => element === document.activeElement), 'Fallback lacks keyboard access');
        await tab.screenshot({ path: `output/playwright/fallback-${width}-js-${javaScriptEnabled}.png` });
        await link.click();
        await tab.waitForURL(target);
        results.push(`PASS fallback and layout: ${width}px, JavaScript ${javaScriptEnabled}`);
      }
      assert(errors.length === 0, `Browser errors: ${errors.join(', ')}`);
    } finally {
      await context.close();
    }
  }
  return results;
}
