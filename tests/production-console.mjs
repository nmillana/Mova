import { chromium, expect } from '@playwright/test';

const browser = await chromium.launch({ channel: 'msedge', headless: true });
const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
const problems = [];

page.on('pageerror', error => problems.push(`pageerror: ${error.message}`));
page.on('console', message => {
  if (message.type() === 'error') problems.push(`console: ${message.text()}`);
});

await page.goto('http://127.0.0.1:5178/', { waitUntil: 'networkidle' });
await expect(page.getByRole('button', { name: 'Crear mi plan personal' })).toBeVisible();
await page.waitForTimeout(2000);
expect(problems).toEqual([]);
console.log(JSON.stringify({ productionLoaded: true, consoleErrors: problems }));
await browser.close();
