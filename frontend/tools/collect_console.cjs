const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox','--disable-setuid-sandbox'] });
  const page = await browser.newPage();

  page.on('console', msg => console.log('PAGE_CONSOLE:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('PAGE_ERROR:', err.message, err.stack));
  page.on('requestfailed', req => console.log('REQUEST_FAILED:', req.url(), req.failure && req.failure().errorText));

  try {
    await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle2', timeout: 15000 });
    // Wait a bit to let the app run
    await page.waitForTimeout(3000);
    // Capture screenshot
    await page.screenshot({ path: '/workspaces/yantrax-rl/frontend/console_capture.png', fullPage: true });
    console.log('Screenshot saved to console_capture.png');
  } catch (e) {
    console.log('NAV_ERROR', e.message);
  }

  await browser.close();
})();